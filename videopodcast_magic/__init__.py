#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Put processed audio back into video files.

    videopodcast-magic                       graphical interface
    videopodcast-magic --help                all switches

Design and rationale: see the manual under docs/ next to this file.
"""

import argparse
import atexit
import bisect
import contextlib
import ctypes
import datetime
import glob
import hashlib
import json
import math
import os
import platform
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import textwrap
from concurrent import futures
import threading
import time
import types


PIECES = {}    # the pieces of the program already read, by their path


class Program(object):
    """This program itself, for a piece of it that reaches back."""


PROGRAM = Program()
PROGRAM.__dict__ = globals()   # the names themselves, never a copy of them


class OneName(types.ModuleType):
    """The program, whose pieces answer to the same names.

    A piece binds the names it uses under its own, so a name bent from
    outside -- which is what a test does, and nothing else does --
    would reach this copy and leave the piece's standing. Bent here, it
    is bent in every piece of this program that carries it.
    """

    def __setattr__(self, name, value):
        types.ModuleType.__setattr__(self, name, value)
        for piece in PIECES.values():
            if "PROGRAM" in piece.__dict__ and name in piece.__dict__:
                piece.__dict__[name] = value


def pieces_answer_together():
    """Let a name bent on this program reach the pieces holding it.

    True where it took. This needs the module as an object, and a run
    that executes the file without registering it under its own name
    leaves none -- such a run bends nothing either, so nothing is lost.
    """
    me = sys.modules.get(__name__)
    if me is None or vars(me).get("__file__") != __file__:
        return False
    me.__class__ = OneName
    return True


def beside(name, program=None):
    """One piece of this program, out of the folder this file lies in.

    Read from its path, and not imported by name. The program is
    started three ways -- installed, as a plain file, and executed from
    an absolute path under a name a test picks -- and an import by name
    finds the piece in the first of them only. A piece given *program*
    gets it before it is read, and binds out of it what it uses.
    """
    import importlib.util
    where = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         name, "__init__.py")
    if where not in PIECES:
        spec = importlib.util.spec_from_file_location(
            "videopodcast_magic." + name, where)
        piece = importlib.util.module_from_spec(spec)
        PIECES[where] = piece
        if program is not None:
            piece.PROGRAM = program
        spec.loader.exec_module(piece)
    return PIECES[where]


def take_from(piece):
    """Bind what a piece brought of its own, under this program.

    A piece is a piece of this program and not a library beside it:
    what it brings answers here under the same name, so that nothing
    outside has to know which file a name ended up in. What it took
    out of the program stands here already and is left alone.
    """
    for name, what in list(piece.__dict__.items()):
        if not name.startswith("__") and name not in globals():
            globals()[name] = what


# ---------------------------------------------------------------------------
# Language
# ---------------------------------------------------------------------------
# Every message is written in English here. A translation lives in the
# folder "language" beside this one, keyed by the English text; T() looks
# it up, and a missing entry shows English rather than a gap.
#
# Adding a language takes three steps:
#   1. Copy language/de.po to the new two-letter code, and name that
#      code at the end of this file.
#   2. Translate every msgstr. Entries left out stay English.
#   3. Nothing else. --lang offers the new code and a system set to it
#      picks it automatically.

language = beside("language")
CATALOGUE = language.CATALOGUE
SOURCE_LANG = language.SOURCE_LANG
LANG = language.LANG
T = language.T
TN = language.TN
known_language = language.known_language
languages = language.languages
system_locale = language.system_locale
texts_of_language = language.texts_of_language


def set_language(name):
    """Switch every message to that language, English if it is unknown.

    The code is held twice: beside this file, where T() reads it, and
    here, which is where a reader of this program and every test look
    for it. One door sets both, so they cannot come apart.
    """
    global LANG
    LANG = language.set_language(name)
    return LANG


def kept_language():
    """The language chosen in an earlier run, or "" if there was none.

    Only a code this program really has texts for counts as a choice.
    What stands under that name in the settings file can be anything
    -- a code from a newer version, one typed in by hand, something
    that is not text at all -- and none of that is anybody's choice:
    it falls through to the system, as if nothing had been written.
    """
    kept = settings().get("language")
    return kept if isinstance(kept, str) and kept in languages() else ""


def group_text(number):
    """Group the thousands the way the chosen language does."""
    return format(int(number), ",d").replace(",", T(","))


def decimal_text(text):
    """Write the decimal point the way the chosen language writes it."""
    mark = T(".")
    return text.replace(".", mark) if mark != "." else text


def channel_text(count):
    """Say a channel count the way a person would.

    One and two have names; above that the number does the work. An
    unreadable file has no count at all, and then a guess would be worse
    than saying so.
    """
    try:
        count = int(count)
    except (TypeError, ValueError):
        return T('channel count unknown')
    return {1: "mono", 2: "stereo"}.get(
        count, TN(count, '%s channel', '%s channels') % group_text(count))


# Set to answer yes before the question is asked: a test run, a build
# machine, anything with nobody in front of it. It answers for both
# places that ask, the package manager and pip -- and nothing installs
# without it, or without somebody saying yes.
INSTALL_TOOLS = bool(os.environ.get("VPM_INSTALL_TOOLS"))


# What this program answers for. It rose to 9.0.1 the day all six
# builder jobs carried it and all three systems had a way of getting
# it offered to them. soxr is no part of it: without soxr the clock
# comes out a hundred times coarser, and coarser is not broken.
FFMPEG_FLOOR = (9, 0, 1)


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
    here = os.path.dirname(os.path.abspath(__file__))
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


# Set by main() before anything else happens, read by the window.
TOOL_TROUBLE = ("", "")


def tools_repaired(kind, says, asked=False):
    """Say what is wrong with ffmpeg, offer the repair, report what is left.

    True where the tools are good afterwards. Everything is said with
    print, so it lands wherever this run shows its output -- the console
    where somebody typed a command line, the log where nobody is
    sitting. *asked* says the question has already been put somewhere
    else, so it is not put a second time.
    """
    print(as_warn(says))
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
        print(as_warn(says))
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


# The floor is what the interface needs: PySide6 does not build below
# 3.10. The command line alone could go lower, but one number is easier
# to state than two. The ceiling is what the suite runs on; between the
# two is untested.
NEEDS_PYTHON = (3, 10)
LIKES_PYTHON = "3.14.7"
if sys.version_info < NEEDS_PYTHON:
    sys.exit("videopodcast-magic needs Python %d.%d or newer -- this is "
             "%d.%d. Recommended version: %s."
             % (NEEDS_PYTHON + sys.version_info[:2] + (LIKES_PYTHON,)))

def only_reading(argv):
    """True where the command line only wants the switch list or the version.

    A question about the command line, asked where the command line is
    read. Reading it needs neither numpy nor ffmpeg.
    """
    return any(a in ("-h", "--help", "--version") for a in argv)


class Numpy:
    """Stands in for numpy until the first calculation asks for it.

    What this file holds must not depend on how the program was
    started, or its parts cannot import one another. Importing it
    fetches nothing; --version answers cheaply because it calculates
    nothing, not because argv was read while the file was being read.
    """

    def __getattr__(self, name):
        global np
        np = _require_module("numpy")
        return getattr(np, name)


np = Numpy()

def count_process_starts(where):
    """Write one line per process this program starts, into a file.

    Process starts are what the Windows builder charges for, so the
    suite counts them per test and prints the count beside the verdict.
    Off unless VPM_COUNT_STARTS names a file. Only Popen is wrapped --
    subprocess.run builds one itself, and wrapping both counted every
    run twice.
    """
    was_popen = subprocess.Popen

    def note(argv):
        first = argv if isinstance(argv, str) else (argv[0] if argv else "?")
        try:
            with open(where, "a", encoding="utf-8") as f:
                f.write("%s\n" % os.path.basename(str(first)))
        except OSError:
            return

    class Popen(was_popen):
        def __init__(self, *a, **k):
            note(a[0] if a else k.get("args") or [])
            was_popen.__init__(self, *a, **k)

    subprocess.Popen = Popen


if os.environ.get("VPM_COUNT_STARTS"):
    count_process_starts(os.environ["VPM_COUNT_STARTS"])


SR = 48000
OUTPUT_SINK = None   # set by the GUI: callable that receives raw log text
GUI_RUNNING = False  # the GUI already lists per-file details, so the log
                     # skips them when this is set
AUDIO_SUFFIXES = (".wav", ".bwf", ".flac", ".aif", ".aiff", ".mp3", ".m4a",
                ".aac", ".ogg", ".opus", ".wv", ".caf")
VIDEO_SUFFIXES = (".mov", ".mp4", ".m4v", ".mxf", ".mkv", ".avi", ".mts",
                 ".m2ts", ".mpg", ".mpeg", ".webm", ".r3d")
TRAILING_NUMBER = re.compile(r"^(.*?)(\d+)$")
VERSION = "3.0.0b4"
PROJECT_PREFIX = "videopodcast-magic_"  # project file: prefix + production
# The names inside the stored files. It counts up whenever a key or
# a stored value is renamed. An older file is refused with a clear
# message rather than read as if it still fitted.
FILE_FORMAT = 3
CEILING_DBTP = -1.0                     # true-peak ceiling of the result
LIMIT_MAX_DB = 6.0        # most the limiter may take off

# What the mixed track is called, one name for both paths. Not only a
# label: the handover file is written with it, Resolve names its audio
# track after it, and reading a handover back looks it up by this word.
MIX_TRACK_NAME = "Full-Mix"

# The switches that need several recordings. Everything else works on any
# run since the two paths became one.
ONLY_MULTITRACK = ("auphonic_resume", "assign", "multitrack")

# Values that are stored and shown at the same time. The value is fixed so
# a project file keeps its meaning in any language; what appears on screen
# comes from CHOICE_LABELS and goes through T().
MIX_ONLY = "mix-only"            # audio track without a camera of its own
IGNORE_AUDIO = "ignore-audio"    # audio track stays out entirely
# The answer "I do not know, go and measure" to the name field's
# question of who is to be heard: a typed name claims one person, this
# says there are several and the machine is to tell them apart.
SEVERAL_SPEAKERS = "several-speakers"
PRESET_NONE = "no-auphonic"      # list entry, not a preset name
TYPE_CONTENT, TYPE_INTRO, TYPE_OUTRO = "content", "intro", "outro"
# The camera nobody sits in front of. A value of the Kind field rather
# than something derived, so it is an answer somebody gives instead of
# a guess -- and it travels in the project file and on the switch.
TYPE_WIDE = "wide-shot"
TYPE_IGNORED = "ignore-video"    # video file stays out entirely
CLIP_TYPES = (TYPE_CONTENT, TYPE_WIDE, TYPE_INTRO, TYPE_OUTRO,
              TYPE_IGNORED)
# Which kinds are a camera in the run. The wide shot is one like any
# other -- aligned, rendered, cut to; the mark says only that no
# speaker belongs to it. Named once here rather than at every place
# that asks "is this a camera".
CAMERA_TYPES = (TYPE_CONTENT, TYPE_WIDE)
# Whether a video file's sound is material for the run. It cannot be
# measured: a radio microphone recorded into the video track looks like
# a room microphone, so only whoever was there knows. Synchronising is
# untouched by it; this decides only whether the sound counts as content.
AUDIO_UNUSED = "audio-unused"
AUDIO_MATERIAL = "audio-material"
AUDIO_USE = (AUDIO_UNUSED, AUDIO_MATERIAL)
# Two names that are easy to confuse: "do not use" leaves the audio out
# entirely, "no camera of its own" only keeps the person off camera.
# The fuller wording is twice as wide as the column allows, so the rest
# of it lives in the tooltip.
CHOICE_LABELS = {MIX_ONLY: "no camera of its own",
                 IGNORE_AUDIO: "do not use",
                 SEVERAL_SPEAKERS: "several speakers",
                 PRESET_NONE: "work without Auphonic",
                 TYPE_CONTENT: "Content", TYPE_INTRO: "Intro",
                 # The same words the cut band, the legend and the four
                 # cut rules use. A second name for one thing would
                 # read as a second thing.
                 TYPE_WIDE: 'Wide shot',
                 TYPE_OUTRO: "Outro", TYPE_IGNORED: "ignore this video",
                 AUDIO_UNUSED: "do not use the audio",
                 AUDIO_MATERIAL: "use the audio"}


def label_of(value):
    """Return what a stored value is called on screen."""
    return T(CHOICE_LABELS[value]) if value in CHOICE_LABELS else value


def fill_choices(box, values, chosen=None):
    """Fill a combo box: it stores the value and shows the label."""
    box.clear()
    for v in values:
        box.addItem(label_of(v), v)
    if chosen is not None:
        pick_choice(box, chosen)


def pick_choice(box, value):
    """Select the entry that stands for this value; first one if unknown."""
    i = box.findData(value)
    box.setCurrentIndex(i if i >= 0 else 0)


# Parallel runs keep per-thread output apart: progress feeds one shared
# bar, text goes to a private buffer and is flushed when the file is done.
THREAD_SHARE = {}    # thread id -> progress fraction of that file
THREAD_BUFFER = {}   # thread id -> list of text chunks

# How much room a file name gets on a button or in a chooser, in
# pixels: wide enough for a recorder's usual name, narrow enough that
# the player on the right stays in the window.
NAME_ROOM = 260
# What the row under the assignment table may take before the player on
# the right is pushed off the window: past this the sheet asks for more
# than a 13 inch screen has.
ROW_ROOM = 380
# How many rows of the speaker table are shown before it scrolls itself.
# Rows, not speakers: one row per speaker plus one for Silence, and the
# column header sits on top. Without a lid the table grew by a row per
# speaker until the Resolve sheet answered with a scroll bar of its own.
SPEAKER_ROWS_SHOWN = 4

# One palette for all three outputs -- GUI, log pane and terminal -- so a
# run looks the same wherever it is watched.
COLOURS = {
    "heading":   "#1f4e79",       # section heading
    "backdrop": "#e8eff7",      # the strip behind a heading
    "good":     "#2e7d4f",       # done
    # Dark enough to clear the 4.5 contrast floor on every surface it
    # stands on, our own and the three desktops'. A lighter orange
    # falls through on the foreign window colours.
    "warning": "#985508",       # warning, run continues
    "error":  "#b02020",       # aborted
    "value":    "#2f5d8a",       # numbers and results
    # Dark enough for the 4.5 contrast floor on the footer, which the
    # desktop paints lighter than our own surfaces.
    "quiet":   "#646e7b",       # secondary
    "text":    "#222222",
    # Surfaces -- GUI only
    "frame":  "#cfd8e3",
    "box":  "#fbfcfe",
    "head":    "#eef2f7",
    "sheet":   "#ffffff",
    "stripe":  "#dce6f2",
    # A switched-off button keeps its own colour, only muted: flat grey
    # reads as a different kind of thing, and the two buttons of a pair
    # then look as if only one were off. The pair still clears the
    # contrast floor, so the label stays readable.
    "off":     "#c6d6e6",       # disabled button: the fill, muted
    "off_text": "#3a5c80",      # disabled button: what stands on it
}

# Same roles for a dark desktop: same hues, lighter and less saturated.
# Saturated colour glares on dark, and a dark blue would be unreadable.
COLOURS_DARK = {
    "heading":   "#7fb4e6",
    "backdrop": "#233040",
    "good":     "#5cc98a",
    # Its own value, and it has to be: the light orange all but
    # disappears against a dark sheet.
    "warning": "#e2a355",
    "error":  "#f07070",
    "value":    "#9dc4e8",
    "quiet":   "#95a1b0",
    "text":    "#e4e8ee",
    "frame":  "#3c4653",
    "box":  "#232a33",
    "head":    "#2b333d",
    "sheet":   "#1d232a",
    "stripe":  "#33404f",
    "off":     "#2c3a48",
    "off_text": "#93a9c0",
}

# The light set kept aside. COLOURS is the one dictionary everything
# reads, so a desktop switched to dark and back has to find the light
# values again -- overwriting them in place would burn the way back.
COLOURS_LIGHT = dict(COLOURS)


def desktop_is_dark(QtWidgets, QtGui):
    """Report whether the desktop uses a dark colour scheme.

    Falls back to the window background lightness where Qt does not
    expose a scheme.
    """
    try:
        schema = QtWidgets.QApplication.styleHints().colorScheme()
        if "Dark" in str(schema):
            return True
        if "Light" in str(schema):
            return False
    except Exception:
        pass
    try:
        return QtWidgets.QApplication.palette().color(
            QtGui.QPalette.Window).lightness() < 128
    except Exception:
        return False
ANSI = {"heading": "\033[1;36m", "good": "\033[1;32m", "warning": "\033[33m",
        "error": "\033[1;31m", "value": "\033[36m", "quiet": "\033[90m",
        "text": ""}


MARK = "\x01"     # invisible prefix; it names the kind of a log line
MARK_KINDS = {"h": "heading", "g": "good", "w": "warning", "e": "error"}


def as_head(text):
    """Mark a line as a section heading."""
    return MARK + "h" + text


def as_good(text):
    """Mark a line as something that worked."""
    return MARK + "g" + text


def as_warn(text):
    """Mark a line as a warning; the run carries on."""
    return MARK + "w" + text


def as_bad(text):
    """Mark a line as an error."""
    return MARK + "e" + text


def split_kind(line):
    """Split a line into its kind and its plain text.

    The kind is stated where the line is written rather than read out of
    its wording, which would tie it to one language. Returns one of
    "heading", "good", "warning", "error", "text".
    """
    if line[:1] == MARK:
        return MARK_KINDS.get(line[1:2], "text"), line[2:]
    return "text", line


def strip_marks(text):
    """Take every kind marker back out of a text."""
    return re.sub(MARK + ".?", "", text) if MARK in text else text


class ColourWriter(object):
    """Colour terminal output without altering the text itself.

    Colour is chosen at the start of a line and held for the rest of it,
    so a progress bar rewriting its line stays intact. The invisible kind
    marker comes off here, so this is in place even without colour.
    """

    def __init__(self, raw, colour=True):
        self.raw = raw
        self.colour = colour
        self.begin = True
        self.pending = False
        self.carried = ""     # marker seen before its line had text

    def write(self, text):
        off = []
        for part in re.split(r"([\n\r])", text):
            if part in ("\n", "\r"):
                if self.pending:
                    off.append("\033[0m")
                    self.pending = False
                off.append(part)
                self.begin = True
            elif part:
                if self.begin:
                    kind, part = split_kind(part)
                    if kind == "text" and self.carried:
                        kind = self.carried
                    if not part:
                        # The marker was in front of a line break, so it
                        # belongs to the line that follows.
                        self.carried = kind
                        continue
                    self.carried = ""
                    code = ANSI.get(kind, "") if self.colour else ""
                    if code:
                        off.append(code)
                        self.pending = True
                    self.begin = False
                else:
                    part = strip_marks(part)
                off.append(part)
        self.raw.write("".join(off))
        self.raw.flush()

    def flush(self):
        self.raw.flush()

    def __getattr__(self, name):
        return getattr(self.raw, name)


def force_utf8_output():
    """Force stdout/stderr to UTF-8.

    Windows consoles default to a legacy code page, where one umlaut in a
    message aborts the run. Replacement characters beat a crash.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def enable_colour_output():
    """Put the output filter in place and colour it where that lands.

    The filter always runs, because it also takes the invisible kind
    markers out again. Colour is added only on a terminal that shows it.
    """
    colour = not os.environ.get("NO_COLOR")
    try:
        colour = colour and bool(sys.stdout.isatty())
    except Exception:
        colour = False
    if colour and os.name == "nt":
        # Windows only shows control characters when asked to.
        try:
            import ctypes
            h = ctypes.windll.kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if not ctypes.windll.kernel32.GetConsoleMode(h,
                                                         ctypes.byref(mode)):
                colour = False
            else:
                ctypes.windll.kernel32.SetConsoleMode(h, mode.value | 0x0004)
        except Exception:
            colour = False
    if getattr(sys.stdout, "keeps_marks", False):
        # The window reads the markers itself and colours by them.
        return
    sys.stdout = ColourWriter(sys.stdout, colour)
    sys.stderr = ColourWriter(sys.stderr, colour)


class Value(object):
    """A value several observers can watch.

    Qt normally binds a value to its input widget. The assignment table is
    rebuilt on every change, so its widgets disappear while the entered
    values must survive. The value lives here and the widget follows it.
    """

    def __init__(self, value=""):
        self._value = value
        self._listeners = []

    def get(self):
        return self._value

    def typed(self):
        """Only the answer given here, with nothing standing in for it.

        The plain reading is get(). This one is for the two places that
        have to tell an answer from a guess: what a widget shows, and
        what is written into the project file. On every value but a
        name field the two are the same string.
        """
        return self._value

    def set(self, value):
        if value == self._value:
            return
        self._value = value
        for f in list(self._listeners):
            try:
                f()
            except Exception:
                pass

    def listen(self, f):
        self._listeners.append(f)
        return f


# What can be shown where "whoever speaks is on screen" gives no
# answer. The names are the values of the four choice fields below and
# of the switches behind them.
SHOT_WIDE = "wide"
SHOT_LISTENER = "listener"
SHOT_ALTERNATE = "alternate"
SHOT_HOLD = "hold"
SHOT_HOLD_BRIEF = "hold-brief"
SHOT_OFF = "off"
SHOT_ANSWER = "answer"

SHOT_NAMES = {
    SHOT_WIDE: 'Wide shot',
    SHOT_LISTENER: 'Listener',
    SHOT_ALTERNATE: 'Alternating',
    SHOT_HOLD: 'No camera change',
    # Holding without an end is a different answer from holding a
    # breath, so the two are two entries and the seconds stand in a
    # field of their own.
    SHOT_HOLD_BRIEF: 'Hold a short gap',
    # Named after what does not happen, not after a switch position:
    # in a row labelled "Question" the picture going early is the only
    # thing there is to leave alone.
    SHOT_OFF: 'do not go early',
    SHOT_ANSWER: 'Answering speaker',
}

# The shortest a shot may stand. A camera that changes faster than the
# viewer can settle on a face reads as nervous. One value for the
# interface, the switch and every default, or the two cut differently.
MIN_EDIT_DURATION_S = 3.0

# Up to here a gap with nobody in it counts as a breath rather than as
# an end, where the cut is told to hold one. Measured over 83 minutes
# on 2.9.2026: at one second no picture stands on a silent person for
# longer than 4.0 s, from two seconds on the first ones over five appear.
SILENCE_HOLD_S = 1.0

# The camera cut is derived from who speaks when; these numbers decide
# how fine it turns out. Per entry: switch, label, default, unit,
# short explanation beside it, longer one in the tooltip.
CUT_FIELDS = (
    ("min-edit-duration", 'Minimum Edit Duration',
     "%.1f" % MIN_EDIT_DURATION_S, "s",
     'shorter shots are merged in',
     'Shorter shots fall into the following one.'),
    ("min-speech-to-switch", 'Speaks at least', "1.5", "s",
     'below this the camera does not follow',
     ('A short "yes" does not move the picture. Without this a block of '
      'half a second draws the camera over, and the minimum edit '
      'duration then holds it there for seconds.')),
    ("silence-hold", 'Short gap up to', "%.1f" % SILENCE_HOLD_S, "s",
     'so long a silence leaves the picture alone',
     ('Only where "Nobody speaks" is set to hold a short gap. A gap up '
      'to this long changes nothing, a longer one goes to the wide '
      'shot. Above two seconds the picture begins to stand on someone '
      'silent for over five seconds.')),
    # Resolve's own name for it, in the German window as well, so it stays
    # English. The double quotes are the mark: this one is not translated.
    ("edit-change-delay", "Edit Change Delay", "0.3", "s",
     'the picture changes this much later than the sound',
     'A negative value makes the picture lead the sound.'),
    ("reaction-lead", 'Answer on screen earlier', "1.5", "s",
     'before the question ends',
     ('Zero is where the asker stops, not where the answer starts: the '
      'pause between them belongs to the question. Applies only where '
      '"After a question" asks for it, and the Edit Change Delay is '
      'not added again.')),
    ("wide-after", 'Wide shot after', "70", "s",
     'from here on a good moment for it is looked for',
     ('The soft limit of the pair: from here the program waits for a '
      'sentence boundary and puts the wide shot there, not on the '
      'clock. 0 turns it off. "Wide shot at the latest" is the hard '
      'limit, where it cuts without one.')),
    ("wide-latest", 'Wide shot at the latest', "120", "s",
     'and here it is cut, good moment or not',
     ('The hard limit of the pair: where no sentence boundary has '
      'turned up since "Wide shot after", the longest speech pause '
      'stands in for one, and at this point the cut happens whatever '
      'is being said.')),
    ("wide-length", 'Wide shot at least', "5", "s",
     'so long the inserted wide shot stands at least',
     ('It then runs to the end of the sentence. Below five seconds the '
      'look reads as a twitch.')),
    ("wide-most", 'Wide shot at most', "15", "s",
     'and at most this long',
     ('Where the end of the sentence lies beyond it, the last clause '
      'break before it ends the shot -- it is not cut off mid-sentence.')),
)

# The cases where the speech does not say whom to show, and what is
# shown instead. Per entry: switch, label, default, the values it
# takes, short explanation beside it, longer one in the tooltip.
CUT_CHOICES = (
    # First, and directly under "Answer on screen earlier": the two
    # belong to one question and used to stand at opposite ends of the
    # tab, in words that did not meet.
    ("on-question", 'After a question', SHOT_ANSWER,
     (SHOT_OFF, SHOT_ANSWER, SHOT_LISTENER),
     'the picture goes to the answer before it starts',
     ('Only after a question that is not the main speaker\'s, when '
      'somebody else takes over at once and keeps the floor.\n"do not '
      'go early" means no early camera change: the picture follows '
      'the sound here as it does everywhere else.')),
    ("on-monologue", 'Long monologue', SHOT_ALTERNATE,
     (SHOT_WIDE, SHOT_LISTENER, SHOT_ALTERNATE, SHOT_HOLD),
     'one person holds the floor past "Wide shot after"',
     ('"Alternating" remembers what the last break of this monologue '
      'showed. The listener only gets the picture when someone on that '
      'camera was heard in the last 20 seconds; otherwise the wide '
      'shot.')),
    ("on-together", 'Several speak at once', SHOT_WIDE,
     (SHOT_WIDE, SHOT_LISTENER, SHOT_ALTERNATE, SHOT_HOLD),
     'and no camera shows exactly them',
     'Cutting into a jumble looks frantic.'),
    # Directly above "Recognition uncertain", because the two were
    # taken for one another: nobody speaking is not the recognition
    # being unsure, and this is the case that decides a fifth of the
    # running time against that one's three thousandths.
    ("on-silence", 'Nobody speaks', SHOT_WIDE,
     (SHOT_WIDE, SHOT_HOLD_BRIEF, SHOT_HOLD),
     'no voice is heard at all here',
     ('A breath in the middle of a sentence and the end of a thought '
      'are both silence, and the program cannot tell them apart. Only '
      'the length can: "Short gap up to" says how long a silence may '
      'be and still count as a breath.')),
    ("on-uncertain", 'Recognition uncertain', SHOT_WIDE,
     (SHOT_WIDE, SHOT_LISTENER, SHOT_ALTERNATE, SHOT_HOLD),
     'the speaker recognition frays or leaves a heap behind',
     ('Guessing puts the wrong person on screen for seconds; the wide '
      'shot is right in every case. Somebody is speaking here -- where '
      'nobody is, "Nobody speaks" decides.')),
)


def shell_quote(cmd):
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode("utf-8", "replace")[-2000:])
    return p


# An ffprobe call costs a process start and, on an external volume, a
# seek out to the disc. Building the interface asks the same questions
# about the same file over and over, and one process each held the
# window thread until the disc answered.
_PROBE = {}


def path_key(path):
    """The one shape a path takes when two of them are compared.

    abspath settles the folder and nothing else: on Windows the same
    file reached two ways keeps the case and the separator it was typed
    with, and compares unequal. normcase settles both, and on a Mac it
    changes nothing. Every comparison and every path used as a key goes
    through here, so the fault where one side is put into shape and the
    other is not cannot be written.
    """
    return os.path.normcase(os.path.abspath(path))


class ByFile(dict):
    """A dictionary of files: one entry per file, whatever it is called.

    The same file arrives typed by hand, out of a file dialogue and out
    of a project file, and on Windows those differ in case while
    meaning one file. Finding therefore goes through path_key on every
    side. The key keeps the spelling it was first written under, so
    what is walked over, shown or saved is the name on the disc.
    """

    # A key that is not a string passes through untouched. A key made
    # of a path and something else is built where it is built, and
    # path_key belongs in that one place -- see prework_api_key.

    def __init__(self, *given, **named):
        dict.__init__(self)
        self._spelt = {}
        if given or named:
            self.update(*given, **named)

    def _index(self):
        """The spelling each file sits under, rebuilt if it is gone.

        A dictionary can come into being without __init__ -- fromkeys,
        a copy read back in -- and a lookup against an index that is
        not there would quietly miss.
        """
        try:
            return self._spelt
        except AttributeError:
            self._spelt = {path_key(k): k for k in self if isinstance(k, str)}
            return self._spelt

    def _as_stored(self, key):
        """The key this file already sits under, or the key itself."""
        if not isinstance(key, str):
            return key
        if dict.__contains__(self, key):
            return key
        return self._index().get(path_key(key), key)

    def __getitem__(self, key):
        return dict.__getitem__(self, self._as_stored(key))

    def __setitem__(self, key, value):
        here = self._as_stored(key)
        dict.__setitem__(self, here, value)
        if isinstance(key, str):
            self._index()[path_key(key)] = here

    def __delitem__(self, key):
        here = self._as_stored(key)
        dict.__delitem__(self, here)
        if isinstance(here, str):
            self._index().pop(path_key(here), None)

    def __contains__(self, key):
        return dict.__contains__(self, self._as_stored(key))

    def __ior__(self, other):
        self.update(other)
        return self

    def get(self, key, fallback=None):
        return dict.get(self, self._as_stored(key), fallback)

    def setdefault(self, key, fallback=None):
        here = self._as_stored(key)
        if dict.__contains__(self, here):
            return dict.__getitem__(self, here)
        self[key] = fallback
        return fallback

    def pop(self, key, *fallback):
        here = self._as_stored(key)
        got = dict.pop(self, here, *fallback)
        if isinstance(here, str):
            self._index().pop(path_key(here), None)
        return got

    def popitem(self):
        key, value = dict.popitem(self)
        if isinstance(key, str):
            self._index().pop(path_key(key), None)
        return key, value

    def clear(self):
        dict.clear(self)
        self._index().clear()

    def update(self, *given, **named):
        for other in given:
            pairs = other.items() if hasattr(other, "items") else other
            for key, value in pairs:
                self[key] = value
        for key, value in named.items():
            self[key] = value

    def copy(self):
        return ByFile(self)


class FileSet(set):
    """A set of files: one entry per file, whatever it is called.

    The companion to ByFile, and for the same reason. Only the members
    that are strings are put into shape; anything else passes through.
    """

    def __init__(self, given=()):
        set.__init__(self)
        self.update(given)

    @staticmethod
    def _shape(item):
        return path_key(item) if isinstance(item, str) else item

    def __contains__(self, item):
        return set.__contains__(self, self._shape(item))

    def add(self, item):
        set.add(self, self._shape(item))

    def discard(self, item):
        set.discard(self, self._shape(item))

    def remove(self, item):
        set.remove(self, self._shape(item))

    def update(self, *given):
        for other in given:
            for item in other or ():
                self.add(item)

    def difference_update(self, *given):
        for other in given:
            for item in other or ():
                self.discard(item)


def file_stamp(path):
    """Identify a file by what changes when it is written to.

    By the real path, not the one the caller typed: a symbolic link
    gives the same file two names and has it measured twice. Nothing
    reads the path back out of this -- it is a key and nothing else --
    so resolving the link costs microseconds and saves a process start.
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


EXT_MARK = "[EXT]"


ENV_MARK = "[ENV]"


BAD_MARK = "[BAD]"


TIME_MARK = "[TIME]"

# When this run began. The bundle a start from the Dock goes through
# puts its own second into VPM_STARTED before it hands over, because
# what happens before Python is running cannot be timed from inside it
# -- and that was exactly the ten seconds nobody could name on 5.9.2026.
_BEGAN = time.time()


def mark_time(what):
    """Write down how far into the start this is.

    Into the log and nowhere else. Five of these say where a slow start
    spends its time, which no amount of reading the source settles.
    """
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
    where sysconfig spells it Lib. Held against each other as text they
    say no about one folder. The path module is an argument so that
    this machine can be asked what another one makes of two names.
    """
    here = paths.normcase(paths.realpath(here))
    folder = paths.normcase(paths.realpath(folder))
    return here.startswith(folder + paths.sep)


def installed_by_a_package_manager():
    """The folder a package manager owns this file in, or "".

    Two things hang on it. An installed copy is not written over by
    the self-update: something else keeps the record of which version
    is there, and writing the file would leave that record wrong. And
    an installed copy does not keep its log beside itself: that folder
    belongs to pip, not to the person running the program.
    """
    import sysconfig
    import site
    # site.USER_SITE, not getusersitepackages(): the call raises where
    # the user folder is switched off, the name is always there, and it
    # is None when there is no such folder.
    owned = [sysconfig.get_paths().get(k) for k in ("purelib", "platlib")]
    owned.append(site.USER_SITE)
    for folder in owned:
        if folder and inside_folder(__file__, folder):
            return folder
    return ""


def log_folder():
    """The folder a log belongs in on this system, or None.

    Neither the cache nor the settings: the cache is the one folder
    everybody is told they may delete, and a setting follows somebody
    to the next machine while a log says what happened on this one.
    Every platform keeps a third place for exactly that, named beside
    each branch below. VPM_LOGS points the whole thing somewhere else.
    """
    base = os.environ.get("VPM_LOGS") or ""
    if base:
        folder = os.path.join(base, "videopodcast-magic")
    elif os.environ.get("VPM_SILENT"):
        # A test run has no business in the log folder of whoever
        # started it, and the suite already points VPM_CACHE at a
        # throwaway. A test with business here names its own VPM_LOGS.
        return cache_folder("logs")
    elif sys.platform == "darwin":
        # What Console.app shows.
        folder = os.path.expanduser("~/Library/Logs/videopodcast-magic")
    elif os.name == "nt":
        # LOCALAPPDATA and not APPDATA: a log must not travel with a
        # roaming profile. Its own folder beside the cache, so that
        # emptying the cache does not take it along.
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

    Beside the program it is found without searching, and that is
    right for a copy somebody downloaded into a folder of their own.
    For an installed copy "beside the program" is site-packages, which
    pip owns: written over at the next install, sometimes read-only,
    and no place for anybody's data. So an installed run writes where
    this system keeps logs, and so does a copy that cannot write.
    """
    if not installed_by_a_package_manager():
        here = os.path.dirname(os.path.abspath(__file__))
        if os.path.isdir(here) and os.access(here, os.W_OK):
            return os.path.join(here, "videopodcast-magic.log")
    folder = log_folder()
    return os.path.join(folder, "videopodcast-magic.log") if folder else None


def log_aside(text):
    """Write one line into the log file only, never to the console.

    What a run prints is read by a person and by the window, and a
    diagnostic line landing between two progress bars tears them
    apart. This goes past both descriptors into the file itself.
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
        # A write that failed once fails again -- a full disc, a file
        # taken away. Stop rather than throw once per line from here.
        _LOG_ASIDE[0] = None


# The same tool on the same file over and over -- the fine measurement
# asks for nine stretches out of two files -- is held back and written
# as one line with the count and the total.
_SAME_AGAIN = {"what": None, "times": 0, "seconds": 0.0}


def outside_say(tool, about, seconds=None, what=None):
    """One line about work that happens outside this program's own code.

    ffmpeg, ffprobe and the two models are where a run spends its
    minutes, and from outside a file read once and a file read four
    times look the same. A stored answer says so too, so every
    measurement in the log is either a call or the line saying why
    there was none.
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

    Keyed on size and modification time: a changed file is measured
    again, one that cannot be stat'ed every time. With *keep* the
    answer outlives the run, which is what a measurement costing half
    a minute needs; *as_json* is for one that is not text.

    A kept answer carries the recipe in its *name* -- see recipe_mark.
    """
    stamp = file_stamp(path)
    if stamp is None:
        return work()
    api_key = (name,) + stamp
    if api_key in _PROBE:
        # Not said. This one is asked thousands of times in a table
        # rebuild, and a line for each would drown the log it is
        # meant to make readable -- and cost more than the lookup.
        return _PROBE[api_key]
    got = probe_kept(api_key) if keep else None
    if got is not None and as_json:
        try:
            got = json.loads(got)
        except Exception:
            got = None          # half a write, or another version
    if got is not None:
        # This one is worth a line: it is the measurement that would
        # otherwise have cost seconds.
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

    Parsed afresh from the remembered text each time, so a caller that
    changes the dictionary cannot affect the next one.
    """
    out = probe_remember("ffprobe", path, lambda: _ffprobe_text(path),
                         keep=True)
    return json.loads(out or b"{}")


def timecode_string(seconds, fps=30.0):
    if seconds < 0:
        seconds = 0.0
    f = int(round((seconds - int(seconds)) * fps))
    s = int(seconds)
    if f >= int(round(fps)):
        f, s = 0, s + 1
    return "%02d:%02d:%02d:%02d" % (s // 3600 % 24, s % 3600 // 60, s % 60, f)


def csv_line(values):
    """One row of a CSV file: comma separated, quoted where it matters.

    Comma and full stop, in every language. These files are read by other
    programs and compared across months; a separator that follows the
    language of the run would make two runs incomparable.
    """
    out = []
    for x in values:
        x = str(x)
        if any(c in x for c in ',";\r\n'):
            x = '"%s"' % x.replace('"', '""')
        out.append(x)
    return ",".join(out) + "\n"


def parse_timecode(s, fps=30.0):
    """Parse '6.4087', '0:06', '1:23:45' or '17:15:56:12' into seconds.

    Drop frame writes the last colon as a semicolon, '17:15:56;12'. That
    is the same value; how the frames are counted is a question for
    timecode_to_frames, not for a length in seconds.
    """
    t = str(s).strip().replace(";", ":")
    p = t.split(":")
    if len(p) == 4:
        return float(p[0]) * 3600 + float(p[1]) * 60 + float(p[2]) + float(p[3]) / fps
    if len(p) == 3:
        return float(p[0]) * 3600 + float(p[1]) * 60 + float(p[2])
    if len(p) == 2:
        return float(p[0]) * 60 + float(p[1])
    return float(t)


def frame_rate_fraction(fps):
    """Return a frame rate as a fraction: 29.97 -> 30000/1001.

    iXML requires a fraction rather than a decimal.
    """
    for whole, num, the_one in ((23.976, 24000, 1001), (29.97, 30000, 1001),
                           (47.952, 48000, 1001), (59.94, 60000, 1001),
                           (119.88, 120000, 1001)):
        if abs(fps - whole) < 0.02:
            return num, the_one
    return int(round(fps)), 1


def is_drop_frame(tc):
    """Report whether a timecode string is drop frame.

    The notation decides, not the frame rate: drop frame uses a semicolon
    before the frames. 29.97 exists in both flavours, so guessing from the
    rate is wrong half the time. No marker means non-drop.
    """
    return ";" in str(tc or "")


def timecode_moved(tc, by_s, fps=30.0):
    """A timecode string moved on by *by_s* seconds.

    Cutting a head off a camera moves the moment its first frame was
    taken, and whoever plays the file reads that moment off the
    timecode. The semicolon of drop frame is kept: losing it turns the
    same frame into a different time of day for whoever reads it.
    """
    moved = timecode_string(parse_timecode(tc, fps) + by_s, fps)
    if is_drop_frame(tc):
        head, _sep, frames = moved.rpartition(":")
        moved = head + ";" + frames
    return moved


def build_ixml(name, tr, fps, bits=24, channels=1, df=False):
    """Build the iXML block for one track.

    Resolve is happy with bext alone, but Premiere and Media Composer fall
    back to iXML. Writing both costs nothing.
    """
    num, the_one = frame_rate_fraction(fps)
    ndf = not df
    tracks = "".join(
        "    <TRACK>\n      <CHANNEL_INDEX>%d</CHANNEL_INDEX>\n"
        "      <INTERLEAVE_INDEX>%d</INTERLEAVE_INDEX>\n"
        "      <NAME>%s</NAME>\n    </TRACK>\n" % (k, k, _xml_escape(name))
        for k in range(1, max(1, channels) + 1))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n<BWFXML>\n'
        '  <IXML_VERSION>1.5</IXML_VERSION>\n'
        '  <PROJECT>%s</PROJECT>\n'
        '  <TAPE>%s</TAPE>\n'
        '  <TAKE>1</TAKE>\n'
        '  <SPEED>\n'
        '    <NOTE>videopodcast-magic</NOTE>\n'
        '    <MASTER_SPEED>%d/%d</MASTER_SPEED>\n'
        '    <CURRENT_SPEED>%d/%d</CURRENT_SPEED>\n'
        '    <TIMECODE_RATE>%d/%d</TIMECODE_RATE>\n'
        '    <TIMECODE_FLAG>%s</TIMECODE_FLAG>\n'
        '    <FILE_SAMPLE_RATE>%d</FILE_SAMPLE_RATE>\n'
        '    <AUDIO_BIT_DEPTH>%d</AUDIO_BIT_DEPTH>\n'
        '    <TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_HI>%d'
        '</TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_HI>\n'
        '    <TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_LO>%d'
        '</TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_LO>\n'
        '  </SPEED>\n'
        '  <TRACK_LIST>\n    <TRACK_COUNT>%d</TRACK_COUNT>\n%s'
        '  </TRACK_LIST>\n</BWFXML>\n'
        % (_xml_escape(name), _xml_escape(name), num, the_one, num, the_one, num, the_one,
           "NDF" if ndf else "DF", SR, bits,
           tr >> 32, tr & 0xFFFFFFFF, max(1, channels), tracks))


def _xml_escape(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def append_ixml(file_path, xml):
    """Append the iXML block as a RIFF chunk and fix up the RIFF size."""
    payload = xml.encode("utf-8")
    if len(payload) % 2:
        payload += b"\x00"
    with open(file_path, "r+b") as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        f.write(b"iXML" + struct.pack("<I", len(payload)) + payload)
        f.seek(4)
        f.write(struct.pack("<I", end + len(payload)))


def parse_time_point(s, fps=30.0):
    """Parse a --in-point/--out-point time.

    Returns (seconds, absolute). Absolute means wall clock since
    midnight, i.e. a timecode; everything else counts from the start of
    the window. A leading plus is optional, a bare number is seconds,
    and a negative value measures back from the window end -- that one
    only for --out-point.
    """
    t = str(s).strip()
    if not t:
        return None, False
    minus = t.startswith("-")
    absolute = t.count(":") >= 2 and not t.startswith(("+", "-"))
    value = parse_timecode(t.lstrip("+-"), fps)
    return (-value if minus else value), absolute


def as_relative_time(seconds):
    """Format a position the way --in-point expects it."""
    ms = int(round(max(0.0, seconds) * 1000))
    s = ms // 1000
    return "+%d:%02d:%02d.%03d" % (s // 3600, s % 3600 // 60, s % 60,
                                   ms % 1000)


def as_hms(sec, mark=None):
    """Write a duration as h:mm:ss with milliseconds.

    *mark* overrides the decimal point. A file that other programs read
    passes ".", so what is in it does not depend on the language.
    """
    # Round to milliseconds first, then split -- otherwise 119.9995 s
    # comes out as "0:01:59.1000".
    ms = int(round(abs(sec) * 1000))
    s = ms // 1000
    return "%s%d:%02d:%02d%s%03d" % ("-" if sec < 0 else "", s // 3600,
                                     s % 3600 // 60, s % 60,
                                     T(".") if mark is None else mark,
                                     ms % 1000)


def sample_count(path):
    """Return the length of a file in samples at the working rate."""
    return probe_remember("samples", path, lambda: _sample_count(path))


def _sample_count(path):
    # Out of the one description of the file rather than a second call
    # of its own: duration_ts counts samples exactly, where a duration
    # in seconds has already been rounded.
    d = ffprobe_json(path)
    a = next((x for x in d.get("streams", [])
              if x.get("codec_type") == "audio"), {})
    try:
        n, sr = int(a["duration_ts"]), int(a.get("sample_rate") or SR)
        return int(round(n * SR / sr)) if sr and sr != SR else n
    except (KeyError, TypeError, ValueError):
        pass
    duration = float(a.get("duration") or d.get("format", {}).get("duration") or 0)
    return int(round(duration * SR))


def bext_time_reference(path):
    """Return TimeReference from the bext chunk in samples, or None."""
    return probe_remember("bext", path, lambda: _bext_time_reference(path))


def _bext_time_reference(path):
    try:
        f = open(path, "rb")
    except OSError:
        return None
    with f:
        if f.read(4) not in (b"RIFF", b"RF64"):
            return None
        f.seek(12)
        while True:
            h = f.read(8)
            if len(h) < 8:
                return None
            cid, sz = h[:4], struct.unpack("<I", h[4:8])[0]
            if cid == b"bext":
                b = f.read(sz)
                return struct.unpack("<Q", b[338:346])[0] if len(b) >= 346 else None
            f.seek(sz + (sz & 1), os.SEEK_CUR)


DAY_S = 24 * 60 * 60


def unwrap_day(value, near):
    """Move *value* by whole days until it sits closest to *near*.

    A timecode starts over at midnight, so a recording running across it
    looks 23 hours away and every difference is out by a day. Nothing is
    added to either axis -- that would make one absolute and the other
    not -- so the two meet only where they are compared. Half a day is
    the fence: past it a night is indistinguishable from a day's gap.
    """
    if value is None or near is None:
        return value
    return value - DAY_S * round((value - near) / float(DAY_S))


def clocks_apart(spans):
    """Which of these time windows share their time with no other.

    *spans* is [(start, length, key), ...] read off the timecode.
    Material from one recording overlaps; a window overlapping with none
    came off a clock never set. All are first brought onto one axis
    around the middle, or a shoot across midnight would look the same.
    Fewer than three say nothing. Returns (apart, moved, placed).
    """
    spans = [(float(a), max(1.0, float(n or 0.0)), k) for a, n, k in spans]
    if len(spans) < 3:
        return set(), [], spans

    def alone(mine, start, wide, among):
        return not any(i != mine and start < b + m and b < start + wide
                       for i, (b, m, _k) in enumerate(among))

    middle = sorted(a for a, _n, _k in spans)[len(spans) // 2]
    moved, placed = [], []
    for i, (a, n, k) in enumerate(spans):
        shifted = unwrap_day(a, middle)
        # A file starting at 00:00:00 is not a recording that began in
        # the first second after midnight, it is a recorder whose clock
        # was never set -- and unwrapping it would drop it neatly among
        # the cameras and hide exactly the fault this is here for.
        if a < 1.0:
            shifted = a
        # Moving a file a whole day is a claim, and only worth making if
        # the file then lands among the others. A recorder left hours
        # out also moves under plain arithmetic and still overlaps
        # nothing, so the move is taken back.
        if shifted != a and not alone(i, shifted, n, spans):
            moved.append(k)
            placed.append((shifted, n, k))
        else:
            placed.append((a, n, k))
    return (set(k for i, (a, n, k) in enumerate(placed)
                if alone(i, a, n, placed)), moved, placed)




def picture_rate(probed):
    """The frame rate of the picture in an ffprobe answer, or nothing.

    ffprobe writes it as a fraction, '30000/1001' for 29.97. The mean
    over the file comes first, because it is frames over duration and
    therefore always a real number; the nominal rate is what the
    container claims and is a timebase in a few odd files.
    """
    v = next((s for s in probed.get("streams", ())
              if s.get("codec_type") == "video"), None)
    for key in ("avg_frame_rate", "r_frame_rate"):
        parts = str((v or {}).get(key) or "").split("/")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            if int(parts[0]) and int(parts[1]):
                return int(parts[0]) / float(int(parts[1]))
    return None


def file_timecode(path, fps=None):
    """Return the start time in seconds from bext or a timecode track.

    The frames of a timecode are frames, so the rate decides what they
    are worth: read at the wrong rate the start lands whole frames out.
    Where no rate is passed the file's own is taken. A sound file has
    none, so its frames belong to the reference picture and a caller who
    knows that rate passes it; without one 30 is the fallback.
    """
    tr = bext_time_reference(path)
    if tr is not None:
        return tr / float(SR)
    d = ffprobe_json(path)
    rate = float(fps) if fps else (picture_rate(d) or 30.0)
    # The tracks before the file: a track's clock is what the camera
    # wrote, the file level is what ffmpeg made of it, and the camera
    # wins where they disagree. A file that keeps a clock nowhere else
    # -- MXF and AVI do -- is still read, only afterwards.
    for source in [s.get("tags", {}) or {} for s in d.get("streams", [])] +\
                  [d.get("format", {}).get("tags", {})]:
        if source.get("timecode"):
            try:
                return parse_timecode(source["timecode"], rate)
            except Exception:
                pass
    return None


#------------------------------------------------------------ Processing

AUPHONIC = "https://auphonic.com"


def api_key_source(args=None):
    """Return (the API key, where it came from).

    Read in order: command line, environment, credential store -- so a
    key in AUPHONIC_TOKEN goes out even where another one is stored.
    Which of the three answered travels with the key: a complaint
    naming the store for a key from elsewhere misdirects the reader.
    """
    given = getattr(args, "auphonic_key", "") if args is not None else ""
    if given:
        return given, "argument"
    from_env = os.environ.get("AUPHONIC_TOKEN")
    if from_env:
        return from_env, "environment"
    kept = load_api_key() or ""
    return kept, ("store" if kept else "")


def key_refused_note(origin, error):
    """Say a key was refused, and name where that key came from."""
    if origin == "environment":
        return T('The key from AUPHONIC_TOKEN is not accepted: %s') % error
    if origin == "store":
        return T('The stored key is not accepted: %s') % error
    return T('auphonic.com does not accept the key: %s') % error


def api_key_from_anywhere(args):
    """Return the API key.

    Checked in order: the command line argument, the environment, the OS
    credential store.
    """
    key = api_key_source(args)[0]
    if not key:
        raise RuntimeError(T('No API key. Pass --auphonic-api-key KEY, set '
                             'AUPHONIC_TOKEN or have it remembered once in '
                             'the interface. The key is in the Auphonic '
                             'account settings.'))
    return key.strip()


def _curl_call(key, arguments, output_binary=False, progress=False):
    """Run curl with the key in a config file rather than in argv.

    In argv the key would be visible in the process list for the duration
    of the call.
    """
    fd, conf = tempfile.mkstemp(prefix="auph_", suffix=".conf")
    os.close(fd)
    leftovers = []
    closing, running = [], []
    try:
        # The one file that holds the key in plain text, and the finally
        # below removes it whatever happened. mkstemp already creates it
        # owner-readable; the chmod says so again for the reader.
        os.chmod(conf, 0o600)
        # curl reads this file as configuration, so the key goes in as a
        # value and not as more configuration: a quotation mark or a line
        # break inside it would otherwise start a directive of its own.
        # curl's own escaping inside a quoted value is a backslash.
        safe = (str(key).replace("\\", "\\\\").replace('"', '\\"')
                .replace("\r", "").replace("\n", ""))
        with open(conf, "w", encoding="utf-8") as f:
            f.write('header = "Authorization: bearer %s"\n' % safe)
        if progress:
            # curl's own bar has no percentage and cannot be indented, so
            # its plain progress table is read and the usual bar drawn
            # from it. The answer goes to a file rather than a pipe: an
            # unread stdout pipe fills up and stalls the transfer.
            fd, body = tempfile.mkstemp(prefix="auph_", suffix=".out")
            os.close(fd)
            leftovers.append(body)
            answer_file = open(body, "wb")
            closing.append(answer_file)
            # Only the connection is limited here, never the
            # transfer: an upload of several gigabytes may take as long
            # as it takes, but a server that never answers at all must
            # not hold the run.
            proc = subprocess.Popen(["curl", "-S", "-L",
                                     "--connect-timeout", "15",
                                     "--config", conf]
                                    + arguments,
                                    stdout=answer_file,
                                    stderr=subprocess.PIPE)
            running.append(proc)
            text = progress if isinstance(progress, str) else T('Transfer')
            rest, last_percent, last_time = "", -1, 0.0
            said = []            # everything that is not a progress line
            show_progress(text, 0.0)
            while True:
                piece = proc.stderr.read(64)
                if not piece:
                    break
                rest += piece.decode("utf-8", "replace")
                parts = re.split(r"[\r\n]", rest)
                rest = parts.pop()
                for line in parts:
                    m = re.match(r"\s*(\d{1,3})\s+\S+\s+\d", line)
                    if not m:
                        # curl -S says here why it gave up.
                        if line.strip():
                            said.append(line.strip())
                        continue
                    pct = min(100, int(m.group(1)))
                    now = time.time()
                    if pct != last_percent and now - last_time > 0.2:
                        show_progress(text, pct / 100.0)
                        last_percent, last_time = pct, now
            proc.wait()
            answer_file.close()
            with open(body, "rb") as fh:
                off = fh.read()
            try:
                os.unlink(body)
            except OSError:
                pass
            show_progress(text, 1.0)
            if OUTPUT_SINK:
                OUTPUT_SINK("\n")
            else:
                sys.stdout.write("\n")
            if rest.strip():
                said.append(rest.strip())
            p = subprocess.CompletedProcess(
                proc.args, proc.returncode, off,
                "\n".join(said[-20:]).encode("utf-8", "replace"))
        else:
            # Long enough for a call that fetches a list of presets,
            # short enough that somebody still believes the window is
            # alive. Without it the button waits for good.
            p = subprocess.run(["curl", "-sS", "-L",
                                "--connect-timeout", "15",
                                "--max-time", "60",
                                "--config", conf] + arguments,
                               capture_output=True)
    finally:
        # A transfer that was broken off leaves curl writing into a file
        # nobody reads any more. It is stopped here, or it would go on
        # downloading gigabytes for a call that has already failed.
        for child in running:
            if child.poll() is None:
                try:
                    child.kill()
                    child.wait(timeout=5)
                except Exception:
                    pass
        for handle in closing:
            try:
                handle.close()
            except Exception:
                pass
        # The config file holds the key, so it goes whatever happened --
        # and a failure to remove it must not replace the real error.
        # Where it cannot be removed it is overwritten first: a file that
        # stays behind should at least not still hold the key.
        for path in [conf] + leftovers:
            try:
                os.unlink(path)
            except FileNotFoundError:
                # Already gone is the goal, not a failure. Without this
                # the branch below made a fresh empty file at that path
                # -- one per upload and one per download, left lying in
                # the temp folder for ever.
                continue
            except OSError:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write("\n")
                except OSError:
                    pass
    if p.returncode:
        error = (p.stderr or b"").decode("utf-8", "replace")[-800:]
        raise RuntimeError(error or T('curl ended with %d') % p.returncode)
    return p.stdout if output_binary else p.stdout.decode("utf-8", "replace")


def _parse_json(text):
    try:
        return json.loads(text)
    except ValueError:
        raise RuntimeError(T('Response was not JSON: %s') % text[:300])


def key_complaint(key):
    """What is wrong with this key before it is sent, or "".

    Only what can be told without asking anybody: whether there is one,
    and whether it looks pasted wrong. The length and character set of a
    real key are not written down here -- a guessed format would turn
    away a key that works. Whether a key is good only auphonic.com knows.
    """
    if not key:
        return T('There is no key.')
    if key != key.strip():
        return T('The key has a space or a line break at one end.')
    if any(c.isspace() for c in key):
        return T('The key is broken in the middle by a space or a line break.')
    if any(ord(c) < 32 or ord(c) == 127 for c in key):
        return T('The key has a character in it that cannot be typed.')
    return ""


def list_presets(key):
    """Fetch the stored presets: (name, uuid, Multitrack or None).

    ``minimal_data=1`` for two reasons: without it the answer is capped
    at ten presets whatever the limit says, and it is the form carrying
    ``is_multitrack``, the field that tells the two kinds apart. An
    unclassified preset comes back as None -- unknown, not ordinary, or
    a Multitrack preset drops out of a list it belongs in.
    """
    d = _parse_json(_curl_call(key, [
        AUPHONIC + "/api/presets.json?minimal_data=1&limit=100"]))
    if d.get("status_code") not in (200, None):
        raise RuntimeError(T('Auphonic reports %s: %s')
                           % (d.get("status_code"), d.get("error_message")))
    items = []
    for p in (d.get("data") or []):
        mark = p.get("is_multitrack")
        items.append((p.get("preset_name") or p.get("name") or T('unnamed'),
                      p.get("uuid") or "",
                      None if mark is None else bool(mark)))
    return items


def preset_fits_mode(mark, multitrack):
    """Does a preset belong in the list for this mode?

    Only a preset we can place is ever thrown out. Where the answer
    carried no mark the kind is unknown, and unknown is shown rather
    than dropped: hiding a preset is worse than one entry too many.
    """
    return mark is None or bool(mark) == bool(multitrack)


def presets_for_mode(key, multitrack):
    """Return only the presets that match the mode.

    A multitrack preset in a plain production (or the other way round)
    produces a production Auphonic refuses to start, so mismatched presets
    are never offered.
    """
    return [(n, u, m) for n, u, m in list_presets(key)
            if preset_fits_mode(m, multitrack)]


def print_presets(key, multitrack=False):
    items = presets_for_mode(key, multitrack)
    if not items:
        print(T('No Multitrack preset found in the account.') if multitrack
              else T('No Singletrack preset found in the account.'))
        return 0
    print("Presets:")
    for i, (name, _, _) in enumerate(items, 1):
        print("  %2d  %s" % (i, name))
    return 0


def choose_preset(key, wanted, multitrack=False, lufs=None,
                   anyway=False):
    """Resolve a preset name to its UUID, asking if there is a choice.

    Both entry paths run through here, so this is where the preset is
    checked against the run. A mismatch raises before anything is uploaded.
    """
    items = presets_for_mode(key, multitrack)
    if not items:
        every = list_presets(key)
        if every:
            raise RuntimeError(
                (T('No Multitrack preset in the account. Only these: %s')
                 if multitrack else
                 T('No Singletrack preset in the account. Only these: %s'))
                % ", ".join(n for n, _, _ in every))
        raise RuntimeError(T('No presets stored in the account. One can be '
                             'created in the web interface.'))
    def done(uuid, name):
        # Checked whatever the loudness is set to. Without a target of
        # ours the loudness comparison stays quiet, but whether a
        # Multitrack preset carries a track template decides whether the
        # tracks come back processed at all.
        findings = check_preset(key, uuid or name, name, lufs, multitrack)
        if report_findings(findings, T('does the preset fit the run?'),
                          anyway):
            raise RuntimeError(T('preset does not fit the run'))
        return uuid or name, name

    if wanted:
        for name, uuid, _ in items:
            if wanted.lower() in (name.lower(), uuid.lower()):
                return done(uuid, name)
        for name, uuid, _m in list_presets(key):
            if wanted.lower() in (name.lower(), uuid.lower()):
                raise RuntimeError(
                    (T('%r is a Singletrack preset, and a Multitrack one '
                       'is needed.') if multitrack else
                     T('%r is a Multitrack preset, and a Singletrack one '
                       'is needed.')) % name)
        print(T('No preset is called %r.') % wanted)
    print(T('Which Auphonic preset should process this file?'))
    for i, (name, uuid, _) in enumerate(items, 1):
        print("  %2d  %s" % (i, name))
    if not sys.stdin.isatty():
        raise RuntimeError(T('No preset given, no input possible. Choose '
                             'one of the above with --auphonic-preset NAME.'))
    while True:
        answer = input(T('  Number (empty = cancel): ')).strip()
        if not answer:
            raise RuntimeError(T('cancelled'))
        if answer.isdigit() and 1 <= int(answer) <= len(items):
            name, uuid, _ = items[int(answer) - 1]
            return done(uuid, name)
        print(T('  Please give a number between 1 and %d.') % len(items))


# Output files with these endings are text about the audio, not audio.
TRANSCRIPT_SUFFIXES = (".json", ".srt", ".vtt", ".txt", ".html", ".xml")

# What may be sent back when a production is updated. The answer to a
# query carries more than that -- size, checksum, download address --
# and sending those back would be describing a file that does not exist
# yet.
OUTPUT_FILE_KEYS = ("format", "ending", "bitrate", "mono_mixdown",
                    "split_on_chapters", "suffix", "filename",
                    "outgoing_services")


# The audio track tag and the recognition language are two different
# code systems: ffmpeg wants three letters after ISO 639-2/B, both
# recognisers the two letter code. Only the plausible ones are listed;
# anything else is passed on as it stands and works itself out.
SPEECH_CODES = {
    "ger": "de", "deu": "de", "eng": "en", "fra": "fr", "fre": "fr",
    "spa": "es", "ita": "it", "nld": "nl", "dut": "nl", "por": "pt",
    "pol": "pl", "rus": "ru", "swe": "sv", "dan": "da", "nor": "no",
    "fin": "fi", "ces": "cs", "cze": "cs", "tur": "tr", "ell": "el",
    "gre": "el", "jpn": "ja", "zho": "zh", "chi": "zh", "kor": "ko",
    "ara": "ar", "heb": "he", "hun": "hu", "ron": "ro", "rum": "ro",
    "ukr": "uk", "cat": "ca",
}


def speech_locale(language):
    """The recogniser's code for the tag the interface carries.

    The Language field and --speech-language hold what ffmpeg wants on
    the audio track: three letters. Both recognisers want the two-letter
    code. "ger" matched no locale and was dropped without a word, so the
    machine's own language decided and the field did nothing -- asked
    for "eng" on a German Mac, the recognition ran in de_DE.
    """
    tag = (language or "").strip()
    return SPEECH_CODES.get(tag.lower(), tag)


# What the interface offers. The tag is what ffmpeg wants on the audio
# track, and the recogniser is told which language to expect.
# Only languages with both are listed -- offering one whose recognition
# code is unknown would promise a transcript that cannot come.
SPOKEN_LANGUAGES = (
    ("ger", "German"), ("eng", "English"), ("fra", "French"),
    ("spa", "Spanish"), ("ita", "Italian"), ("nld", "Dutch"),
    ("por", "Portuguese"), ("pol", "Polish"), ("rus", "Russian"),
    ("swe", "Swedish"), ("dan", "Danish"), ("nor", "Norwegian"),
    ("fin", "Finnish"), ("ces", "Czech"), ("tur", "Turkish"),
    ("ell", "Greek"), ("hun", "Hungarian"), ("ron", "Romanian"),
    ("ukr", "Ukrainian"), ("cat", "Catalan"), ("ara", "Arabic"),
    ("heb", "Hebrew"), ("jpn", "Japanese"), ("zho", "Chinese"),
    ("kor", "Korean"),
)


def spoken_language_choices():
    """Return [(tag, name)] for the language field, by name."""
    return sorted(((tag, T(name)) for tag, name in SPOKEN_LANGUAGES),
                  key=lambda x: x[1].lower())


def language_of_system():
    """Return the track tag the system language suggests, or "".

    Only a suggestion for the empty field: the operating system does not
    know what language was spoken in a recording.
    """
    # The locale is read directly, not through known_language: that
    # one answers which language the *interface* speaks and falls back
    # to English. A Spanish system would then suggest English, and the
    # recording would be tagged wrongly.
    head = (system_locale() or "").replace("_", "-").split("-")[0]
    head = head.strip().lower()
    if len(head) != 2:
        return ""
    for tag, _name in SPOKEN_LANGUAGES:
        if SPEECH_CODES.get(tag) == head:
            return tag
    return ""


def output_file_wish(f):
    """Reduce an output file entry to what may be asked for again."""
    return {k: f[k] for k in OUTPUT_FILE_KEYS if f.get(k) is not None}


def wishes_then_start(key, uuid, stereo=False):
    """Set what the simple API cannot, then start the production.

    The simple API takes a file and a preset and nothing else; keeping
    two channels is not in it. It is settled in one call, and that call
    starts the production -- one created without "action=start" waits
    for exactly this. The existing output files are read and sent back,
    or the audio the preset asks for goes.
    """
    if not stereo:
        return
    d = _parse_json(_curl_call(
        key, [AUPHONIC + "/api/production/%s.json" % uuid]))
    already = ((d.get("data") or {}).get("output_files") or [])
    wish = [output_file_wish(f) for f in already]
    request = {}
    if stereo:
        # The preset decides whether the mixdown is folded to one channel.
        # With a stereo recording that fold cannot be undone afterwards, so
        # the flag is cleared on every output the preset asks for.
        for f in wish:
            if f.get("mono_mixdown"):
                f["mono_mixdown"] = False
    request["output_files"] = wish
    request["action"] = "start"
    fd, js = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        with open(js, "w", encoding="utf-8") as f:
            json.dump(request, f, ensure_ascii=False)
        answer = _parse_json(_curl_call(
            key, ["-X", "POST", "-H", "Content-Type: application/json",
                  AUPHONIC + "/api/production/%s.json" % uuid, "-d", "@" + js]))
    finally:
        os.unlink(js)
    if answer.get("status_code") not in (200, 201, None):
        raise RuntimeError(T('Auphonic will not take the settings: '
                             '%s') % (answer.get("error_message")
                                      or answer.get("form_errors")))
    if stereo:
        print(T('  Two channels requested -- the recording is stereo'))


def run_single_production(audio, preset, presetname, key, target_folder,
                  wait_s=7200, dry_run=False, title=None):
    """Upload a file, start the production, wait, download the result."""
    title = title or os.path.splitext(os.path.basename(audio))[0]
    size = os.path.getsize(audio) / 1e6
    stereo = kept_channels(audio) == 2
    # What the file really has, not what the run keeps of it:
    # kept_channels answers one for anything above two, which would
    # call a four channel recording mono in the log. Only the wording
    # changes here, not what happens to the file.
    try:
        really = int(channel_count(audio))
    except (OSError, ValueError, RuntimeError):
        really = kept_channels(audio)
    print(as_head(T('PROCESSING AT AUPHONIC.COM:')))
    print(T('  Preset:  %s') % presetname)
    print(T('  File:    %s (%s, %s)') % (os.path.basename(audio),
                              as_data_size(size),
                              channel_text(really)))
    if really > 2:
        print(as_warn(T('  More than two channels go to auphonic.com as '
                        'one: the fold is only switched off for stereo.\n'
                        '  Where the channels are meant to stay apart, '
                        'cut the file into tracks first.')))
    if dry_run:
        print(T('  (measuring only: nothing uploaded)\n'))
        return None
    # With a stereo recording the production is created but not started:
    # the mono fold has to be switched off, and that is a second call.
    # Without it the production starts straight away.
    later = stereo
    make = ["-X", "POST", AUPHONIC + "/api/simple/productions.json",
            "-F", "preset=%s" % preset,
            "-F", "title=%s" % title,
            "-F", "input_file=@%s" % audio]
    if not later:
        make.insert(-2, "-F")
        make.insert(-2, "action=start")
    answer = _curl_call(key, make,
                   progress=T('Uploading %s') % os.path.basename(audio))
    d = _parse_json(answer)
    if d.get("status_code") not in (200, 201, None):
        raise RuntimeError(T('Auphonic reports %s: %s')
                           % (d.get("status_code"), d.get("error_message") or
                              d.get("form_errors") or answer[:300]))
    data = d.get("data") or d
    uuid = data.get("uuid")
    if not uuid:
        raise RuntimeError(T('no production id in the response: %s') % answer[:300])
    wishes_then_start(key, uuid, stereo)
    print(T('  Production running (%s)') % uuid)

    started = time.time()
    last, horizon = None, 150.0        # a guess: two and a half minutes,
                                       # doubling from there
    end = started + wait_s
    # The same waiting the multitrack production does, and the same
    # function: one production is watched like several.
    p = wait_for_production(key, uuid, wait_s)

    files = p.get("output_files") or []
    if not files:
        raise RuntimeError(T('production finished, but no output file'))
    def rank(f):
        # Lossless before lossy, in case the preset delivers several.
        nm = (f.get("filename") or "").lower()
        return {".wav": 1, ".flac": 2, ".aiff": 3}.get(os.path.splitext(nm)[1], 9)
    best = sorted(files, key=rank)[0]
    name = best.get("filename") or (title + ".wav")
    url = best.get("download_url")
    if not url:
        raise RuntimeError(T('no download address for %s') % name)
    os.makedirs(target_folder, exist_ok=True)
    target = os.path.join(target_folder, name)
    _curl_call(key, ["-o", target, url],
          progress=T('Downloading %s') % name)
    if os.path.getsize(target) < 1000:
        raise RuntimeError(T('downloaded file is only %s bytes')
                           % group_text(os.path.getsize(target)))
    print(T('  Result: %s (%s) -- stays next to the video file\n')
          % (os.path.basename(target), as_data_size(os.path.getsize(target) / 1e6)))
    fetch_text_outputs(key, files, target_folder, skip=best)
    return target


def fetch_text_outputs(key, files, target_folder, skip=None):
    """Fetch what a production wrote about the audio, not the audio.

    Transcript, subtitles, chapter marks: paid for with the production
    either way, and useless if they stay on the server.
    """
    fetched = set()
    for f in files or []:
        if f is skip:
            continue
        name = f.get("filename") or ""
        url = f.get("download_url")
        if not name or not url:
            continue
        if not name.lower().endswith(TRANSCRIPT_SUFFIXES):
            continue
        # Two outputs of the same name land in the same file, so the
        # second download overwrites the first and both were paid for.
        # It happens where a production carries the same format twice.
        if name in fetched:
            print(T('  %s is there already -- not fetched twice') % name)
            continue
        fetched.add(name)
        target = os.path.join(target_folder, name)
        try:
            _curl_call(key, ["-o", target, url],
                       progress=T('Downloading %s') % name)
            print(T('  Also fetched: %s') % name)
        except Exception as e:
            print(T('  %s could not be fetched: %s') % (name, e))


def size_in_mb(file_path):
    try:
        return os.path.getsize(file_path) / 1e6
    except OSError:
        return 0.0


def as_data_size(mb_value):
    """Format a byte count for reading: 542 MB, 1,024 MB, 28.9 GB."""
    if mb_value >= 1000:
        return decimal_text("%.1f GB" % (mb_value / 1000.0))
    return "%s MB" % group_text(math.ceil(mb_value))


def audio_summary(file_path):
    """Return key facts about an audio file as (label, value) pairs."""
    d = ffprobe_json(file_path)
    a = next((x for x in d.get("streams", []) if x.get("codec_type") == "audio"), {})
    if str(a.get("sample_fmt", "")).startswith("flt"):
        depth = "32 bit float"
    else:
        depth = "%s bit" % (a.get("bits_per_raw_sample")
                            or a.get("bits_per_sample") or "?")
    channels = channel_text(a.get("channels"))
    tc = file_timecode(file_path)
    # Read at the file's own rate, so shown at it too: at 25 the frames
    # of the timecode are worth 1/25 s, and a line printed at 30 would
    # give the file back a timecode it never carried.
    rate = picture_rate(d) or 30.0
    return [("Format", "%s, %s, %s Hz, %s" % (a.get("codec_name", "?"), depth,
                                              a.get("sample_rate", "?"), channels)),
            (T('Length'), "%s  (%s)  --  %s"
             % (as_hms(sample_count(file_path) / float(SR)), as_data_size(size_in_mb(file_path)),
                "Timecode %s" % timecode_string(tc, rate) if tc is not None
                else T('no timecode')))]


MOV_CONTAINERS = (b"moov", b"trak", b"mdia", b"minf", b"stbl", b"wave")


def _mov_atoms(f, end):
    """Enumerate atoms between the current offset and end.

    Yields (kind, start of payload, end of atom) per atom.
    """
    while True:
        begin = f.tell()
        if begin + 8 > end:
            return
        head = f.read(8)
        if len(head) < 8:
            return
        size = struct.unpack(">I", head[:4])[0]
        kind = head[4:8]
        if size == 1:
            raw = f.read(8)
            if len(raw) < 8:
                return
            size = struct.unpack(">Q", raw)[0]
        elif size == 0:
            size = end - begin
        if size < 8:
            return
        stop = min(end, begin + size)
        yield kind, f.tell(), stop
        f.seek(stop)


def _read_colr_atom(f, end, depth=0):
    if depth > 8:
        return None
    for kind, content, stop in _mov_atoms(f, end):
        if kind == b"colr":
            f.seek(content)
            raw = f.read(min(19, stop - content))
            if len(raw) >= 10 and raw[:4] in (b"nclc", b"nclx"):
                prim, trc, mat = struct.unpack(">HHH", raw[4:10])
                full = (bool(raw[10] & 0x80)
                        if raw[:4] == b"nclx" and len(raw) >= 11 else None)
                return prim, trc, mat, full
            continue
        if kind in MOV_CONTAINERS:
            f.seek(content)
            hit = _read_colr_atom(f, stop, depth + 1)
            if hit:
                return hit
        elif kind == b"stsd":
            # Version, flags, count, then the entries.
            f.seek(content + 8)
            for _kind2, content2, end2 in _mov_atoms(f, stop):
                # Video entry: 78 bytes of fixed header, then sub-atoms.
                if end2 - content2 <= 78:
                    continue
                f.seek(content2 + 78)
                hit = _read_colr_atom(f, end2, depth + 1)
                if hit:
                    return hit
    return None


def colour_arguments(source, extend=False):
    """Pass the source colour tags through explicitly.

    With -c:v copy ffmpeg rewrites the colr box from its own values and
    replaces anything it does not know, so Resolve no longer recognises
    the input colour space. With fill_gaps=True one gap some cameras
    leave is closed: a BT.2020 matrix with unspecified primaries makes
    the primaries BT.2020 too. Nothing is invented.
    """
    values = mov_colour_tags(source)
    if not values:
        return []
    prim, trc, mat, full = values
    if extend and prim == 2 and mat == MATRIX_BT2020:
        prim = PRIMARIES_BT2020
    opts = ["-color_primaries", str(prim), "-color_trc", str(trc),
          "-colorspace", str(mat)]
    if full is not None:
        opts += ["-color_range", "pc" if full else "tv"]
    return opts


def camera_metadata(file_path):
    """Read the camera's QuickTime metadata keys.

    They name the device and app used. Resolve reads them; without them
    it cannot tell that a phone recorded in log, because the colr box of
    those files reports the transfer function as unspecified. Only the
    com. keys, because these have to reach the new file unchanged, and a
    plain key such as encoder is rewritten by whatever wrote it.
    """
    try:
        d = ffprobe_json(file_path)
    except Exception:
        return {}
    tags = ((d or {}).get("format") or {}).get("tags") or {}
    return {k: v for k, v in tags.items() if k.startswith("com.")}


# The one data track ffmpeg writes whole. mebx -- what an iPhone writes
# -- and camm, rtmd and fdsc arrive with an empty sample description.
# And never tmcd: ffmpeg then drops the timecode this program worked
# out, and the camera lands in the wrong place on the common axis.
DATA_TAGS_TO_KEEP = ("gpmd",)


def data_track_tags(file_path):
    """The tags of the file's data tracks, in the order ffprobe gives them."""
    try:
        d = ffprobe_json(file_path)
    except Exception:
        return []
    return [(s.get("codec_tag_string") or "?").strip()
            for s in (d or {}).get("streams", [])
            if s.get("codec_type") == "data"]


def data_track_maps(file_path):
    """The -map arguments for the data tracks that may be carried over."""
    out = []
    for i, tag in enumerate(data_track_tags(file_path)):
        if tag in DATA_TAGS_TO_KEEP:
            out += ["-map", "0:d:%d" % i]
    return out


def check_data_tracks(source, target):
    """Report which of the camera's data tracks reached the new file.

    The timecode track is not counted: this program writes one of its
    own, so it is replaced rather than lost.
    """
    a = [t for t in data_track_tags(source) if t != "tmcd"]
    if not a:
        return
    b = data_track_tags(target)
    kept = [t for t in a if t in b]
    left = [t for t in a if t not in DATA_TAGS_TO_KEEP]
    if left:
        print(as_warn(T('  Data tracks:     %s left out -- ffmpeg cannot '
                        'write it') % ", ".join(left)))
    if kept:
        print(T('  Data tracks:     %s carried over') % ", ".join(kept))


# What the container says about itself and who wrote it. Every rewrite
# moves these, and none of them came off a camera, so counting them
# would claim camera data the camera never wrote.
CONTAINER_TAGS = ("major_brand", "minor_version", "compatible_brands",
                  "encoder")


def file_metadata(file_path):
    """Every metadata key of the file, minus what the container owns."""
    try:
        d = ffprobe_json(file_path)
    except Exception:
        return {}
    tags = ((d or {}).get("format") or {}).get("tags") or {}
    return {k: v for k, v in tags.items() if k.lower() not in CONTAINER_TAGS}


def check_camera_metadata(source, target):
    """Report whether the camera metadata keys survived the copy.

    Every key the source carries, not only the Apple ones: a camera
    writing none of those used to get no line at all. Presence is
    compared and not the value, because some values change on purpose
    -- the timecode is worked out afresh -- and a check reading those
    as a loss would cry wolf on every run.
    """
    a, b = file_metadata(source), file_metadata(target)
    if not a:
        print(T('  Camera data:     the source carries none'))
        return
    missing = [k for k in a if k not in b]
    if not missing:
        print(T('  Camera data:     %s keys carried over (%s)')
              % (group_text(len(a)), a.get("com.apple.quicktime.model")
                 or a.get("model")
                 or a.get("com.apple.quicktime.software") or "..."))
    else:
        print(as_warn(T('  Camera data:     Caution, %s of %s keys are '
                        'missing in the new file: %s')
                      % (group_text(len(missing)), group_text(len(a)),
                         ", ".join(missing[:4]))))
        print(T('                   Resolve may then not recognise the '
                'input colour space.'))


# Atoms in the sample description that ffmpeg drops when copying but
# Resolve reads. For iPhone recordings "logs" holds the recording
# curve, e.g. "com.apple.apple-wide-gamut.apple-log", which is how
# Resolve recognises Apple Log 2. The colr box says nothing about it.

# "gama" is the curve of older QuickTime recordings, "dvcC" and "dvvC"
# the Dolby Vision set. Not "st3d": ffmpeg writes a vexu box of its own
# beside it, and the two together make a file nothing will open, while
# every check in copy_mov_atoms passes.
ATOMS_TO_COPY = (b"logs", b"gama", b"dvcC", b"dvvC")


def _atom_boxes(data, start, end):
    """Return the boxes of one MOV level.

    Yields (start, size, kind, header length) per box.
    """
    i = start
    while i + 8 <= end:
        size = struct.unpack(">I", data[i:i + 4])[0]
        kind = data[i + 4:i + 8]
        head = 8
        if size == 1:
            if i + 16 > end:
                return
            size = struct.unpack(">Q", data[i + 8:i + 16])[0]
            head = 16
        elif size == 0:
            size = end - i
        if size < head or i + size > end:
            return
        yield i, size, kind, head
        i += size


def _find_atom(data, start, end, kind):
    for i, size, a, head in _atom_boxes(data, start, end):
        if a == kind:
            return i, size, head
    return None


def _video_track_chain(data, moov_i, moov_size, moov_head):
    """Return the video trak box and the chain down to its sample entry."""
    for t_i, t_size, t_kind, t_head in _atom_boxes(data, moov_i + moov_head,
                                           moov_i + moov_size):
        if t_kind != b"trak":
            continue
        mdia = _find_atom(data, t_i + t_head, t_i + t_size, b"mdia")
        if not mdia:
            continue
        hdlr = _find_atom(data, mdia[0] + mdia[2], mdia[0] + mdia[1],
                           b"hdlr")
        # hdlr: four bytes version and flags, four reserved, then the kind
        # of track.
        if not hdlr or data[hdlr[0] + hdlr[2] + 8:
                             hdlr[0] + hdlr[2] + 12] != b"vide":
            continue
        minf = _find_atom(data, mdia[0] + mdia[2], mdia[0] + mdia[1],
                           b"minf")
        if not minf:
            continue
        stbl = _find_atom(data, minf[0] + minf[2], minf[0] + minf[1],
                           b"stbl")
        if not stbl:
            continue
        stsd = _find_atom(data, stbl[0] + stbl[2], stbl[0] + stbl[1],
                           b"stsd")
        if not stsd:
            continue
        # In stsd: four bytes version/flags, four bytes count, then entries.
        entry = next(_atom_boxes(data, stsd[0] + stsd[2] + 8,
                              stsd[0] + stsd[1]), None)
        if not entry:
            continue
        return [(moov_i, moov_head), (t_i, t_head), (mdia[0], mdia[2]),
                (minf[0], minf[2]), (stbl[0], stbl[2]), (stsd[0], stsd[2]),
                (entry[0], entry[3])]
    return None


def _top_level_boxes(file_path):
    out = []
    total = os.path.getsize(file_path)
    with open(file_path, "rb") as f:
        pos = 0
        while pos < total - 8:
            f.seek(pos)
            head = f.read(8)
            if len(head) < 8:
                break
            size, kind = struct.unpack(">I4s", head)
            if size == 1:
                size = struct.unpack(">Q", f.read(8))[0]
            elif size == 0:
                size = total - pos
            if size < 8:
                break
            out.append((kind, pos, size))
            pos += size
    return out


# A sample description atom is an identifier, not a payload. Anything
# larger is left alone, because then the assumption no longer holds.
ATOM_LIMIT = 64 * 1024


def _verify_mov_after_edit(file_path, moov_pos, moov_old_size, above_before_value, for_it):
    """Verify the file survived the edit. An empty result means it did.

    Checked against the state before: same top level boxes at the same
    offsets, moov still last and reaching the end of file, the chain down to
    the video sample entry readable again, and the intended atoms present.
    """
    try:
        total = os.path.getsize(file_path)
        above = _top_level_boxes(file_path)
        if not above:
            return T('boxes no longer readable')
        if above[-1][0] != b"moov" or above[-1][1] != moov_pos:
            return T('moov is no longer in its place')
        if above[-1][1] + above[-1][2] != total:
            return T('moov no longer ends at the end of the file')
        if [(a, i, g) for a, i, g in above[:-1]] != \
                [(a, i, g) for a, i, g in above_before_value[:-1]]:
            return T('the media data is no longer where it was')
        if above[-1][2] <= moov_old_size:
            return T('moov has not grown')
        with open(file_path, "rb") as f:
            f.seek(above[-1][1])
            moov = f.read(above[-1][2])
        chain = _video_track_chain(moov, 0, len(moov), 8)
        if not chain:
            return T('the video track can no longer be found')
        e_i, e_head = chain[-1]
        e_size = struct.unpack(">I", moov[e_i:e_i + 4])[0]
        present = {bytes(a) for _i, _g, a, _k
                in _atom_boxes(moov, e_i + e_head + 78, e_i + e_size)}
        missing = [a.decode("latin1") for a in for_it if a not in present]
        if missing:
            return T('did not arrive: %s') % ", ".join(missing)
        # Every level has to fit exactly inside its parent, otherwise some
        # size field is wrong.
        for idx in range(len(chain) - 1):
            i, head = chain[idx]
            size = struct.unpack(">I", moov[i:i + 4])[0]
            kind_i, kind_head = chain[idx + 1]
            kind_size = struct.unpack(">I", moov[kind_i:kind_i + 4])[0]
            if not (i + head <= kind_i and kind_i + kind_size <= i + size):
                return T('a box no longer fits into its parent')
    except Exception as e:
        return T('cannot be read back (%s)') % str(e)[:60]
    return ""


def copy_mov_atoms(source, target, kinds=ATOMS_TO_COPY):
    """Copy sample description atoms from the source into the new file.

    Copied byte for byte, nothing synthesised, and only where moov sits
    at the end of the target: growing it then moves no media data and
    every offset stays valid. The result is verified and the old moov
    put back on any mismatch -- better without the atom than with a file
    nothing will open. Returns the atoms copied, [] where none were.
    """
    # Folders, missing paths and empty names occur here, and copying
    # atoms is a side step: they end it quietly rather than raise.
    for file_path in (source, target):
        if not file_path or not os.path.isfile(file_path):
            return []
    absent = []
    src_top = _top_level_boxes(source)
    src_moov = next(((p, g) for a, p, g in src_top if a == b"moov"), None)
    if not src_moov:
        return []
    with open(source, "rb") as f:
        f.seek(src_moov[0])
        src = f.read(src_moov[1])
    chain = _video_track_chain(src, 0, len(src), 8)
    if not chain:
        return []
    e_i, e_head = chain[-1]
    e_size = struct.unpack(">I", src[e_i:e_i + 4])[0]
    src_kind = bytes(src[e_i + 4:e_i + 8])       # hvc1, avc1, apcn ...
    existing = {}
    # The sub-atoms sit behind the box header and 78 bytes of fixed
    # fields of the video entry.
    for i, size, kind, head in _atom_boxes(src, e_i + e_head + 78,
                                   e_i + e_size):
        if kind not in kinds:
            continue
        if size > ATOM_LIMIT:
            print(T('  Atom %s skipped: %s bytes are too much for it.')
                  % (kind.decode("latin1"), group_text(size)))
            continue
        existing[kind] = src[i:i + size]
    if not existing:
        return []

    dst_top = _top_level_boxes(target)
    if not dst_top or dst_top[-1][0] != b"moov":
        print(T('  Cannot add atoms: moov is not at the end.'))
        return []
    dst_pos, dst_size = dst_top[-1][1], dst_top[-1][2]
    with open(target, "rb") as f:
        f.seek(dst_pos)
        dst = bytearray(f.read(dst_size))
    if len(dst) != dst_size:
        return []
    # The old moov stays in place: if the verification fails, it comes
    # back exactly as it was.
    old_moov = bytes(dst)
    chain = _video_track_chain(dst, 0, len(dst), 8)
    if not chain:
        return []
    e_i, e_head = chain[-1]
    e_size = struct.unpack(">I", dst[e_i:e_i + 4])[0]
    dst_kind = bytes(dst[e_i + 4:e_i + 8])
    if dst_kind != src_kind:
        # An atom from an HEVC description does not belong in an H.264 one.
        # The boxes fit, the contents do not.
        print(T('  Cannot add atoms: the source is %s, the target %s.') % (src_kind.decode("latin1", "replace"),
                       dst_kind.decode("latin1", "replace")))
        return []
    already = {bytes(kind) for _i, _g, kind, _k
             in _atom_boxes(dst, e_i + e_head + 78, e_i + e_size)}
    fresh = b"".join(v for k, v in existing.items() if k not in already)
    if not fresh:
        return []
    # Every box enclosing the entry grows.
    for i, _head in chain:
        size = struct.unpack(">I", dst[i:i + 4])[0]
        if size == 1:
            print(T('  Cannot add atoms: a 64 bit box is in the way.'))
            return []
        struct.pack_into(">I", dst, i, size + len(fresh))
    insert = e_i + e_size

    def moov_write(content):
        with open(target, "r+b") as f:
            f.seek(dst_pos)
            f.write(content)
            f.truncate(dst_pos + len(content))
            f.flush()
            os.fsync(f.fileno())

    for_it = [k for k in existing if k not in already]
    try:
        moov_write(bytes(dst[:insert]) + fresh + bytes(dst[insert:]))
        damage = _verify_mov_after_edit(target, dst_pos, dst_size, dst_top, for_it)
    except Exception as e:
        damage = T('while writing: %s') % str(e)[:60]
    if damage:
        try:
            moov_write(old_moov)
            back = T('the old moov is back in place')
        except Exception as e:
            back = T('ROLLBACK FAILED (%s)') % str(e)[:60]
        print(T('  Adding atoms taken back -- %s. %s')
              % (damage, back))
        return []
    return [k.decode("latin1") for k in for_it]


def _logs_atom_text(file_path):
    """Return the text of the video track logs atom, or ""."""
    try:
        above = _top_level_boxes(file_path)
        spot = next(((p, g) for a, p, g in above if a == b"moov"), None)
        if not spot:
            return ""
        with open(file_path, "rb") as f:
            f.seek(spot[0])
            moov = f.read(spot[1])
        chain = _video_track_chain(moov, 0, len(moov), 8)
        if not chain:
            return ""
        e_i, e_head = chain[-1]
        e_size = struct.unpack(">I", moov[e_i:e_i + 4])[0]
        for i, size, kind, head in _atom_boxes(moov, e_i + e_head + 78, e_i + e_size):
            if kind == b"logs":
                return moov[i + head:i + size].decode("latin1", "replace")
    except Exception:
        pass
    return ""


# The atom holds a reverse domain name whose middle piece is the colour
# space; no digit anywhere says which of the two curves it is.
LOG_ATOM_NAMES = {"com.apple.rec2020.apple-log": "Apple Log (Rec.2020)",
                  "com.apple.apple-wide-gamut.apple-log":
                      "Apple Log 2 (Apple Wide Gamut)"}


def log_curve_from_atom(text):
    """Return the recording curve named by the logs atom.

    The name carries the colour space too: the same curve is recorded in
    two of them, and a table built for one lays the wrong space on the
    other. Known identifiers get a plain name, anything else is shown
    verbatim -- an unknown identifier is information, an invented name
    would not be.
    """
    raw = (text or "").replace("\x00", " ").strip()
    if not raw:
        return ""
    return LOG_ATOM_NAMES.get(raw.lower(), raw)


def check_colour_survived(source, target, extend=False):
    """Report whether the written file carries the intended colour tags.

    Compared against the intended values, not against the source: missing
    primaries are filled in from the matrix, so the box is meant to differ.
    """
    a, b = mov_colour_tags(source), mov_colour_tags(target)
    if a is None and b is None:
        return
    want = a
    if a and extend and a[0] == 2 and a[2] == MATRIX_BT2020:
        want = (PRIMARIES_BT2020,) + tuple(a[1:])
    if b == want and want != a:
        print(T('  Colour:          %d/%d/%d -- primaries filled in from '
                'the matrix (source: %d)') % (want[0], want[1], want[2], a[0]))
        return
    if a == b:
        print(T('  Colour:          %d/%d/%d carried over') % a[:3])
        return
    print(as_warn(T('  Colour:          Caution, %s in the source, %s in '
                    'the new file') % (a[:3] if a else T('nothing'), b[:3] if b else T('nothing'))))
    print(T('                   Resolve may then not recognise the input '
            'colour space.'))


def mov_colour_tags(file_path):
    """Read the colr box of a MOV file.

    Returns (primaries, transfer, matrix, full range) or None. ffprobe
    is not used: it reports names rather than numbers and names a wrong
    one for values it does not know, Apple Log among them. Only the atom
    tree is walked, so a huge recording is skipped over rather than read.
    """
    try:
        size = os.path.getsize(file_path)
        with open(file_path, "rb") as f:
            return _read_colr_atom(f, size)
    except (OSError, struct.error):
        return None


def video_summary(file_path, info):
    v = info["video"]
    tags = info.get("tags") or {}
    # The nominal rate comes first: editors use it. The measured one
    # beside it where it differs -- frame count over track duration, so a
    # property of the container.
    label_text, measured = info.get("nominal") or info["fps"], info["fps"]
    lines = [("Video", "%s, %sx%s, %s fps%s%s"
               % (v.get("codec_name", "?"), v.get("width"), v.get("height"),
                  decimal_text("%.3f" % label_text),
                  "" if abs(measured - label_text) < 0.0005
                  else T('  (container; measured %s)')
                  % decimal_text("%.4f" % measured),
                  "" if known_frame_rate(file_frame_rate(info))
                  else T('  --  no Resolve Timeline runs at this rate; '
                         'it is converted'))),
              (T('Length'), "%s  (%s)  --  %s"
               % (as_hms(info["duration"]), as_data_size(size_in_mb(file_path)),
                  "Timecode %s" % info["tc"] if info["tc"]
                  else T('no timecode'))),
              (T('Colour'), colour_text(file_path, v, tags)),
              (T('Camera'), camera_text(tags))]
    if info["audio"]:
        a = info["audio"][0]
        channels = channel_text(a.get("channels"))
        count = len(info["audio"])
        lines.append((T('Camera audio'),
                      TN(count, '%s track, %s, %s Hz, %s',
                         '%s tracks, %s, %s Hz, %s')
                      % (group_text(count), a.get("codec_name", "?"),
                         a.get("sample_rate", "?"), channels)))
    else:
        lines.append((T('Camera audio'), T('no audio track present')))
    return lines


def print_key_values(lines, indent="  "):
    # The column follows the longest label, so it holds in every language.
    width = max([len(k) for k, _ in lines] or [9]) + 1
    for k, value in lines:
        print("%s%-*s %s" % (indent, width, k + ":", value))


def print_audio_details(file_path, indent="  "):
    print_key_values(audio_summary(file_path), indent)


def print_video_details(file_path, info, indent="  "):
    print_key_values(video_summary(file_path, info), indent)


def open_in_file_manager(file_path):
    """Show a folder in Finder, Explorer or the desktop file manager."""
    folder = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
    try:
        if sys.platform == "darwin":
            if os.path.isdir(file_path):
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["open", "-R", file_path])
        elif os.name == "nt":
            if os.path.isdir(file_path):
                os.startfile(folder)
            else:
                # The switch and the path have to be one single argument,
                # otherwise Explorer opens the documents folder.
                subprocess.Popen('explorer /select,"%s"'
                                 % os.path.normpath(file_path))
        else:
            subprocess.Popen(["xdg-open", folder])
        return True
    except Exception:
        return False


def report_timecode_check(audio_start, info, measured, indent="  "):
    """Compare what the timecode says with what can be heard."""
    if audio_start is None or not info["tc"]:
        return
    fps = max(1.0, info["fps"])
    loud_tc = unwrap_day(parse_timecode(info["tc"], fps),
                         audio_start) - audio_start
    deviation = measured - loud_tc
    print(T('%sTimecode check of the audio file') % indent)
    if not GUI_RUNNING:
        print(T('%s  Audio starts per timecode at    %s')
              % (indent, timecode_string(audio_start, fps)))
        print(T('%s  Picture starts per timecode at  %s')
              % (indent, timecode_string(parse_timecode(info["tc"], fps), fps)))
    print(T('%s  Offset per timecode:            %s') % (indent, as_hms(loud_tc)))
    print(T('%s  Offset measured:                %s') % (indent, as_hms(measured)))
    if abs(deviation) > 60:
        print(T('%s  Deviation:                      %s') % (indent, as_hms(deviation)))
        print(T('%s  The audio timecode does not fit the picture at all -- '
                'probably a clock never set. The measurement is used.')
              % indent)
    elif abs(deviation) > 0.5 / fps:
        print(T('%s  Deviation:                      %s  (%s frames)')
              % (indent, as_hms(deviation),
                 decimal_text("%.1f" % (abs(deviation) * fps))))
        print(T('%s  The timecode does not fit what is heard. The '
                'measurement is used.') % indent)
    else:
        print(T('%s  Deviation:                      %s  (%s frames) -- fits')
              % (indent, as_hms(deviation),
                 decimal_text("%.1f" % (abs(deviation) * fps))))


#---------------------------------------------------------- Collecting files

# Date and time in a file name: "r_260808_185628" is the eighth of August
# 2026 at 18:56:28. Six digits for the date or eight, six for the time.
NAME_CLOCK = re.compile(r"(?<![0-9])([0-9]{6}|[0-9]{8})[_\-. ]([0-9]{6})"
                        r"(?![0-9])")
# How far the clock in the name may sit from where the previous block ends.
# Recorders write whole seconds, and the length of a block is rarely a
# whole one, so two seconds of slack are needed -- and two blocks that
# really follow one another are never further apart than that.
CLOCK_SLACK = 2.0
# How far two blocks of one recording may sit apart per timecode. A
# recorder that closes one file and opens the next needs a fraction of
# a second; one that stood between the two can be minutes.

# Half an hour is the fence because a clock is set wrong by whole
# hours -- a time zone, or the twelve of AM against PM -- so half of
# the smallest of those catches every one and still lets a real pause
# through. Without a fence a gap of 12:19:48 joined (1.9.2026).
BLOCK_GAP_MAX_S = 1800.0
# What a track cut out of a multichannel file is called at the end. The
# search for continuation blocks has to leave those alone: the number in
# them is a channel, not a block.
SPLIT_MARK = re.compile(r"_Channel\d+(?:\+\d+)?$")


def clock_in_name(name):
    """Return the moment a file name carries: (seconds, before, after).

    Recorders that number their files leave a counter the search for
    continuations can step; mixers write the date and time of day
    instead, which is not a counter and has to be read as a clock and
    held against the length of the block before it. *before* and *after*
    are the rest of the name, so only names built alike are compared.
    """
    m = NAME_CLOCK.search(name)
    if not m:
        return None
    day, clock = m.group(1), m.group(2)
    shape = "%y%m%d" if len(day) == 6 else "%Y%m%d"
    try:
        when = datetime.datetime.strptime(day + clock, shape + "%H%M%S")
    except ValueError:
        return None
    # Naive on purpose: both names come from the same recorder and the
    # same evening, and only their difference is used.
    return (when.replace(tzinfo=datetime.timezone.utc).timestamp(),
            name[:m.start()], name[m.end():])


def blocks_by_clock(file_path):
    """Find the blocks of one recording by the clock in their names.

    Only files built exactly the same way count: same folder, same
    extension, the same text before and after the clock. Of those, the
    one whose clock sits where the previous block ends is the next.
    """
    folder = os.path.dirname(file_path) or "."
    name, ext = os.path.splitext(os.path.basename(file_path))
    mine = clock_in_name(name)
    if not mine:
        return [file_path], []
    when, before, after = mine
    family = {}
    try:
        every = os.listdir(folder)
    except OSError:
        return [file_path], []
    doubled, both = set(), {}
    for f in sorted(every):
        stem, kind = os.path.splitext(f)
        if kind.lower() != ext.lower():
            continue
        other = clock_in_name(stem)
        if not other or other[1] != before or other[2] != after:
            continue
        if other[0] in family:
            # Two files claiming the same moment -- "260808" and
            # "20260808" spell the same day. Which one is meant cannot be
            # decided here, so neither is taken.
            doubled.add(other[0])
            both.setdefault(other[0],
                            [os.path.basename(family[other[0]])]).append(f)
            continue
        family[other[0]] = os.path.join(folder, f)
    said = []
    for moment in doubled:
        family.pop(moment, None)
        for name in both.get(moment, []):
            said.append((name, T('two file names for the same moment -- '
                                 'neither of them is taken')))
    if len(family) < 2 or when not in family:
        return [file_path], said
    row, discarded = [file_path], list(said)

    def follows(a, b):
        """Does the block at moment b start where the one at a ends?"""
        fits, _why = shapes_match(family[a], family[b])
        if not fits:
            return False
        length = sample_count(family[a]) / float(SR)
        return abs((a + length) - b) <= CLOCK_SLACK

    times = sorted(family)
    here = when
    while True:                                   # forwards
        later = [t for t in times if t > here]
        if not later:
            break
        step = later[0]
        if not follows(here, step):
            fits, why = shapes_match(family[here], family[step])
            discarded.append((os.path.basename(family[step]),
                              why if not fits else
                              T('does not start where the block before it '
                                'ends')))
            break
        row.append(family[step])
        here = step
    here = when
    while True:                                   # backwards
        earlier = [t for t in times if t < here]
        if not earlier:
            break
        step = earlier[-1]
        if not follows(step, here):
            fits, why = shapes_match(family[step], family[here])
            discarded.append((os.path.basename(family[step]),
                              why if not fits else
                              T('ends before the next block starts')))
            break
        row.insert(0, family[step])
        here = step
    return row, discarded


def _joins_seamlessly(before, after, row):
    """Report whether `after` continues `before` seamlessly.

    Returns (yes, reason). With timecode: the next block starts where the
    previous one ends. Without timecode only the block size is left -- a
    block short of full size is an end of recording, followed by a pause of
    unknown length.
    """
    fits, why = shapes_match(before, after)
    if not fits:
        return False, why
    t_before, t_after = file_timecode(before), file_timecode(after)
    if t_before is not None and t_after is not None:
        gap = t_after - (t_before + sample_count(before) / float(SR))
        # A pause is known and filled with silence on assembly, so a
        # short one is no problem. A long one is not a pause but a
        # clock that was never set: joined, it becomes hours of silence
        # inside the file, and nothing afterwards takes it out again.
        if gap > BLOCK_GAP_MAX_S:
            return False, (T('gap of %s per timecode, too far apart for '
                             'one recording') % as_hms(gap))
        return gap > -1.0, (T('overlap of %s per timecode')
                               % as_hms(abs(gap)))
    # The candidate belongs in the comparison, or the very first step
    # compares a block with itself and always says yes: a finished short
    # take before the real recording would be glued on.
    sizes = [os.path.getsize(p) for p in row]
    sizes += [os.path.getsize(before), os.path.getsize(after)]
    return (os.path.getsize(before) >= 0.98 * max(sizes),
            T('previous block is shorter than the rest'))


def find_continuation_files(file_path):
    """Find every block of the same recording, forwards and backwards.

    Only seamless continuations are appended, and the same test applies
    both ways, so it makes no difference whether the first block or a
    middle one is picked.
    """
    folder = os.path.dirname(file_path) or "."
    name, ext = os.path.splitext(os.path.basename(file_path))
    # A track cut out of a multichannel file ends in a channel number,
    # and looking for the next number would find the next channel. Those
    # are not blocks of one recording, they are different microphones.
    if SPLIT_MARK.search(name):
        return [file_path], []
    # A clock in the name is the more specific reading and comes first:
    # where it is there, the trailing digits are a time of day and
    # stepping them by one would look for a file a second later.
    by_clock = None
    if clock_in_name(name):
        row, discarded = blocks_by_clock(file_path)
        if len(row) > 1:
            return row, discarded
        # Nothing joined by the clock. It may be the session start,
        # written into every block, with the real index in a counter
        # behind it. So the counter rule gets its turn; what the clock
        # found is kept in case the counter finds nothing either.
        by_clock = (row, discarded)
    m = TRAILING_NUMBER.match(name)
    if not m:
        return by_clock or ([file_path], [])
    stem, digits = m.group(1), m.group(2)
    width = len(digits)
    row, discarded = [file_path], []
    # Exactly as they are written, and no other spelling: on a
    # case-sensitive disc REC0002.wav and rec0002.wav are two files, and
    # taking one for the other answers differently depending on the
    # folder listing. Two spellings in a row is two naming logics.
    every = set(os.listdir(folder))

    def neighbour(index_number):
        for b in (width, 0):
            nm = ("%s%0*d%s" % (stem, b, index_number, ext)) if b else\
                 ("%s%d%s" % (stem, index_number, ext))
            if nm in every:
                return os.path.join(folder, nm)
        return None

    index_number = int(digits)
    while True:                                   # forwards
        index_number += 1
        candidate = neighbour(index_number)
        if not candidate:
            break
        matches, reason = _joins_seamlessly(row[-1], candidate, row)
        if not matches:
            discarded.append((os.path.basename(candidate), reason))
            break
        row.append(candidate)

    index_number = int(digits)
    while index_number > 0:                             # backwards
        index_number -= 1
        candidate = neighbour(index_number)
        if not candidate:
            break
        matches, reason = _joins_seamlessly(candidate, row[0], row)
        if not matches:
            discarded.append((os.path.basename(candidate), reason))
            break
        row.insert(0, candidate)
    if len(row) == 1 and by_clock and by_clock[1]:
        # The counter found nothing either; then what the clock had to
        # say about the neighbours is the better answer.
        return by_clock
    return row, discarded


def track_order_for_camera(own, every, singles=()):
    """Return the audio tracks for one camera, in order.

    Track 1 is the finished mix of what belongs to this camera, so
    taking only the first is correct. Then the same speakers, the
    overall mix minus the crosstalk, and last the camera microphone.
    *singles* get a line of their own where nobody was assigned here;
    every line is the name the track carries in the written file.
    """
    sequence = []
    if own:
        sequence.append('Mix %s' % " + ".join(own)
                     if len(own) > 1 else own[0])
        if len(own) > 1:
            sequence += list(own)
    else:
        sequence.append(MIX_TRACK_NAME)
        sequence += list(singles)
    if every and own and set(own) != set(every):
        sequence.append(MIX_TRACK_NAME)
    sequence.append("Camera Original")
    return sequence


# What must not go from a preset into a production: identifiers,
# times, states. Everything else is adopted, including fields
# Auphonic adds later, so nothing has to be maintained here.
PRESET_READ_ONLY = (
    "uuid", "preset_name", "creation_time", "change_time", "status",
    "status_string", "error_status", "error_message", "warning_status",
    "warning_message", "image", "thumbnail", "length", "length_timestring",
    "waveform_image", "status_page", "edit_page", "start_allowed",
    "change_allowed", "in_review", "chapters", "preset", "is_multitrack")


def read_preset(key, uuid):
    """Fetch one preset in full."""
    d = _parse_json(_curl_call(key, [AUPHONIC + "/api/preset/%s.json" % uuid]))
    if d.get("status_code") not in (200, None):
        raise RuntimeError(T('Preset not readable: %s') % d.get("error_message"))
    return d.get("data") or d


def find_output_format(key, find, avoid=()):
    """Find an Auphonic output format by its name.

    The identifiers are undocumented, so they are looked up rather than
    guessed: /api/info/output_files.json lists every output format with
    its identifier and name.
    """
    try:
        d = _parse_json(_curl_call(key, [AUPHONIC + "/api/info/output_files.json"]))
    except Exception:
        return None
    kinds = d.get("data")
    if isinstance(kinds, dict):
        kinds = [dict(v, format=k) for k, v in kinds.items()
                 if isinstance(v, dict)]
    if not isinstance(kinds, list):
        kinds = []
    for a in kinds:
        if not isinstance(a, dict):
            continue
        text = " ".join(str(a.get(f) or "")
                        for f in ("format", "string", "name")).lower()
        if all(word in text for word in find) and not any(word in text
                                                      for word in avoid):
            return {"format": a.get("format"),
                    "ending": a.get("ending") or ""}
    return None


def missing_outputs(existing, wanted):
    """Return the output formats still missing from a production.

    Auphonic appends rather than replaces on update: sending a format that
    already exists leaves it in the production twice, and it is billed and
    computed twice.
    """
    def fingerprint(e):
        return (str((e or {}).get("format") or "").lower(),
                str((e or {}).get("suffix") or "").lower(),
                bool((e or {}).get("mono_mixdown")))
    present = set()
    for e in (existing or []):
        if not isinstance(e, dict):
            continue
        present.add(fingerprint(e))
        # The response carries the format but no suffix; the file name
        # has it. Where the channel count is not stated both readings
        # count as present -- an upload sent twice is computed and
        # billed twice, and that is the worse mistake.
        name = str(e.get("filename") or "")
        stem = os.path.splitext(name)[0]
        kind = str(e.get("format") or "").lower()
        said = e.get("mono_mixdown")
        both = (bool(said),) if said is not None else (True, False)
        if "_" in stem:
            suffix = "_" + stem.rsplit("_", 1)[1].lower()
            for mono in both:
                present.add((kind, suffix, mono))
        elif e.get("suffix"):
            # An output that is configured but not rendered yet has no
            # file name to read a suffix from. It carries its own.
            for mono in both:
                present.add((kind, str(e["suffix"]).lower(), mono))
    absent = []
    for e in wanted:
        if fingerprint(e) in present:
            continue
        present.add(fingerprint(e))
        absent.append(e)
    return absent


def master_output_format(key, stereo=False):
    """Request the finished mixdown as well -- 24 bit WAV.

    Not needed as audio but as a yardstick: it shows how loud our own
    mix of the same tracks should end up, and it costs no extra credit
    because the production is computed anyway. One channel would be
    enough and half the download, but only while every track is mono --
    with a stereo track the yardstick would sit decibels off the mix.
    """
    kind = (find_output_format(key, ("wav-24bit",))
           or find_output_format(key, ("wav",), avoid=("zip", "tracks")))
    if not kind or not kind.get("format"):
        return None
    entry = {"format": kind["format"], "ending": kind.get("ending") or "wav",
               "mono_mixdown": not stereo, "suffix": "_master"}
    return entry


def build_multitrack_request(preset, title, names, base_name, key=None,
                             stereo=False):
    """Build the production request from the preset that was read.

    The preset cannot simply be sent along: Auphonic then merges its
    tracks with ours and the production stays incomplete. So it is read
    and its contents adopted, except what we set ourselves. The first
    preset track's settings apply to all of ours, leaving the count free.
    """
    request = {k: v for k, v in preset.items() if k not in PRESET_READ_ONLY}
    template = {}
    for track in (preset.get("multi_input_files") or []):
        template = dict(track.get("algorithms") or {})
        break
    request["is_multitrack"] = True
    request["multi_input_files"] = [
        {"type": "multitrack", "id": n, "algorithms": dict(template)}
        for n in names]
    # We choose the output ourselves: the single tracks only. The mixdown
    # is built from them afterwards to match the cameras.
    request["output_files"] = [{"format": "tracks", "ending": "wav.zip"}]
    if key:
        # The finished mixdown comes along as a yardstick: it shows how loud
        # our own mix should end up.
        mst = master_output_format(key, stereo)
        if mst:
            request["output_files"].append(mst)
            print(as_good(T('  Finished mixdown requested as the yardstick '
                            '(%s)')
                          % mst["format"]))
            if stereo:
                print(T('  Two channels, because one track is stereo'))
    request["metadata"] = dict(preset.get("metadata") or {})
    request["metadata"]["title"] = title
    request["output_basename"] = base_name
    return request


def find_production_by_title(key, title):
    """Return the Auphonic production with this title, or None."""
    d = _parse_json(_curl_call(key, [AUPHONIC + "/api/productions.json?limit=50"]))
    wanted_name = (title or "").strip().lower()
    for p in (d.get("data") or []):
        if ((p.get("metadata") or {}).get("title") or "").strip().lower()\
                == wanted_name:
            return p
    return None


def print_production(p):
    """Print what a production already contains."""
    tracks = p.get("multi_input_files") or []
    uploaded = [(x.get("id"), x.get("input_file")) for x in tracks]
    done = [f.get("filename") for f in (p.get("output_files") or [])
              if f.get("download_url")]
    print("  Status:      %s" % (p.get("status_string") or "?"))
    print(T('  Created:     %s') % (p.get("creation_time") or "?")[:19].replace(
        "T", " "))
    if uploaded:
        print(T('  Uploaded:'))
        for fingerprint, file in uploaded:
            print("    %-20s %s" % (fingerprint, file or T('-- nothing --')))
    if done:
        print(T('  Results:'))
        for n in done:
            small = (n or "").lower()
            if small.endswith(".zip"):
                what = T('the individual tracks, packed')
            elif small.endswith(".wav"):
                what = T('the finished mixdown')
            else:
                what = ""
            print("    %-46s %s" % (n, what))
    else:
        print(T('  Results:     none'))
    # Without the tracks nothing works, without the mixdown the loudness
    # has no yardstick. Left unsaid, a missing one turns "reuse" into a
    # dead end.
    small = [(n or "").lower() for n in done]
    has_zip = any(n.endswith(".zip") for n in small)
    has_master = any(n.endswith(".wav") for n in small)
    missing = []
    if not has_zip:
        missing.append(T('the individual tracks'))
    if not has_master:
        missing.append(T('the mixdown as the yardstick'))
    if missing:
        # Always the production at auphonic.com, not the local disk --
        # everything is downloaded again anyway.
        print(T('  Missing:     %s') % ", ".join(missing))
    return all(d for _, d in uploaded) and bool(uploaded), has_zip, missing


def update_production(key, uuid, request):
    """Bring an existing production's settings up to the preset.

    Uploaded files stay in place: Auphonic matches tracks by identifier and
    that does not change. Presets can therefore be tried out without
    uploading again -- only the upload costs credit, not the computation.
    """
    fd, js = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    without_output = dict(request)
    try:
        with open(js, "w", encoding="utf-8") as f:
            json.dump(without_output, f, ensure_ascii=False)
        answer = _parse_json(_curl_call(key, ["-X", "POST", "-H",
                                    "Content-Type: application/json",
                                    AUPHONIC + "/api/production/%s.json" % uuid,
                                    "-d", "@" + js]))
    finally:
        os.unlink(js)
    if answer.get("status_code") not in (200, 201, None):
        raise RuntimeError(T('Change rejected: %s')
                           % (answer.get("error_message")
                              or answer.get("form_errors")))
    return answer.get("data") or {}


def read_production(key, uuid):
    """Fetch the current state of a production."""
    return (_parse_json(_curl_call(key, [AUPHONIC + "/api/production/%s.json" % uuid]))
            .get("data") or {})


def update_track(key, uuid, track_id, algorithms):
    """Change the settings of a single track.

    Auphonic only matches a track through its own URL. Sending the track
    list to the production appends instead of matching -- three tracks
    become six, the second three without a file.
    """
    fd, js = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        with open(js, "w", encoding="utf-8") as f:
            json.dump({"id": track_id, "type": "multitrack",
                       "algorithms": algorithms}, f, ensure_ascii=False)
        answer = _parse_json(_curl_call(key, [
            "-X", "POST", "-H", "Content-Type: application/json",
            AUPHONIC + "/api/production/%s/multi_input_files/%s.json"
            % (uuid, track_id), "-d", "@" + js]))
    finally:
        os.unlink(js)
    if answer.get("status_code") not in (200, 201, None):
        return str(answer.get("error_message")
                   or answer.get("form_errors") or T('rejected'))
    return None


def update_all_tracks(key, uuid, wanted, existing):
    """Bring the tracks of an existing production up to the preset.

    *wanted* is the track list from our request: one identifier and the
    preset settings per track. Each track is addressed individually.
    Returns (changed, unchanged, errors).
    """
    present = dict((str(t.get("id")), t) for t in
              (existing.get("multi_input_files") or []))
    error, changed, same = [], [], []
    for entry in wanted:
        fingerprint = str(entry.get("id"))
        want = entry.get("algorithms") or {}
        old = present.get(fingerprint)
        if old is None:
            error.append(T('%s: not there') % fingerprint)
            continue
        if dict(old.get("algorithms") or {}) == dict(want):
            same.append(fingerprint)
            continue
        bad = update_track(key, uuid, fingerprint, want)
        if bad:
            error.append("%s: %s" % (fingerprint, bad))
        else:
            changed.append(fingerprint)
    return changed, same, error


def run_multitrack_production(key, preset_uuid, title, tracks, target_folder,
                        wait_s=7200, dry_run=False, carry_on=None):
    """Create a multitrack production, upload, wait, fetch the tracks.

    Returns {speaker name: path of the processed file}.
    """
    step_begin("auphonic")
    names = [track["name"] for track in tracks]
    base = safe_filename(title)
    print(as_head(T('PROCESSING AT AUPHONIC.COM (MULTITRACK):')))
    print(T('  Production:  %s') % title)
    print(T('  Tracks:      %s') % ", ".join(names))
    total = sum(os.path.getsize(track["axis"]) for track in tracks) / 1e6
    print(T('  To upload:   %s') % as_data_size(total))
    if dry_run:
        print(T('  (measuring only: nothing uploaded)\n'))
        return {}

    preset = read_preset(key, preset_uuid)
    if not preset.get("is_multitrack"):
        raise RuntimeError(T('%r is not a Multitrack preset')
                           % preset.get("preset_name"))
    stereo = widest_track([track["axis"] for track in tracks]) == 2
    request = build_multitrack_request(preset, title, names, base, key,
                                       stereo)

    # --- does this production already exist?
    existing = find_production_by_title(key, title)
    if existing:
        return reuse_production(key, existing, request, preset,
                                          tracks, names, target_folder, base,
                                          wait_s, carry_on)
    fd, js = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        with open(js, "w", encoding="utf-8") as f:
            json.dump(request, f, ensure_ascii=False)
        answer = _parse_json(_curl_call(key, ["-X", "POST", "-H",
                                    "Content-Type: application/json",
                                    AUPHONIC + "/api/productions.json",
                                    "-d", "@" + js]))
    finally:
        os.unlink(js)
    if answer.get("status_code") not in (200, 201, None):
        raise RuntimeError(T('Auphonic reports %s: %s')
                           % (answer.get("status_code"),
                              answer.get("error_message")
                              or answer.get("form_errors")))
    p = answer.get("data") or {}
    uuid = p.get("uuid")
    if not uuid:
        raise RuntimeError(T('no production id in the response'))
    created = [x.get("id") for x in (p.get("multi_input_files") or [])]
    if sorted(created) != sorted(names):
        raise RuntimeError(T('Auphonic created different tracks than '
                             'requested: %s instead of %s') % (created, names))
    print(T('  Production running (%s)') % uuid)

    upload_args = ["-X", "POST", AUPHONIC + "/api/production/%s/upload.json" % uuid]
    for track in tracks:
        upload_args += ["-F", "%s=@%s" % (track["name"], track["axis"])]
    d = _parse_json(_curl_call(
        key, upload_args,
        progress=T('Uploading %s tracks') % group_text(len(tracks))))
    absent = [x.get("id") for x in ((d.get("data") or {}).get(
        "multi_input_files") or []) if not x.get("input_file")]
    if absent:
        raise RuntimeError(T('These tracks got no file: %s')
                           % ", ".join(absent))

    _curl_call(key, ["-X", "POST",
                AUPHONIC + "/api/production/%s/start.json" % uuid])
    p = wait_for_production(key, uuid, wait_s)

    return download_results(key, p, names, target_folder, base)


def download_results(key, p, names, target_folder, base):
    """Download a finished production: the single tracks."""
    zip_file = None
    for f in (p.get("output_files") or []):
        if (f.get("filename") or "").lower().endswith(".zip"):
            zip_file = f
            break
    if not zip_file:
        raise RuntimeError(T('Production finished, but no ZIP with the '
                             'individual tracks'))
    cache = tracks_folder(target_folder)
    target = os.path.join(cache, zip_file.get("filename"))
    _curl_call(key, ["-o", target, zip_file.get("download_url")],
          progress=T('Downloading %s') % zip_file.get("filename"))
    # Whatever else the preset produces -- chapter marks, transcript,
    # analyses -- belongs here too. It is paid for either way.
    already = set()
    for f in (p.get("output_files") or []):
        name = f.get("filename") or ""
        if not name or not f.get("download_url") or f is zip_file:
            continue
        if name.lower() in already:
            # Two output kinds with the same file name: the second would only
            # overwrite the first. Once is enough.
            print(T('  %s is in the production twice -- fetched once.')
                  % name)
            continue
        already.add(name.lower())
        extra_file = os.path.join(cache, name)
        try:
            _curl_call(key, ["-o", extra_file, f["download_url"]],
                  progress=T('Downloading %s') % name)
        except Exception as e:
            print(T('  %s could not be fetched: %s') % (name, e))
    return match_zip_entries_to_tracks(target, names, target_folder)


def find_pauses(tracks):
    """Merge all speech blocks and return the gaps between them."""
    every = sorted((a, b) for _, segs in tracks for a, b in segs)
    merged = []
    for a, b in every:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    pauses = [(merged[i][1], merged[i + 1][0])
              for i in range(len(merged) - 1)]
    entries_in = {n: sorted(a for a, _ in segs) for n, segs in tracks}
    return pauses, entries_in


# =====================================================================
#  What the cut is decided by -- the rules a human editor follows on
#  top of "whoever speaks is on screen". Every number is adjustable.
# =====================================================================









































































































def format_complaint(d):
    """Say why a stored file cannot be used, or return "".

    The file carries the number of the naming it was written with. Where
    that differs, the keys inside mean something else -- reading it anyway
    would look like it worked and quietly assign the wrong things.
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








































































































ASK_SINK = None   # set by the GUI: callable(options, title) -> key


def ask_choice(possible, heading, title=T('Question'), default_value=None,
               switch="--auphonic-resume"):
    """Ask a question -- in the terminal, in the GUI or via a switch.

    *options* is a list of (key, text) and the key is returned. *switch* is
    the command line switch that preselects the answer; it appears in the
    error message when nobody is there to answer.
    """
    print("\n  %s" % heading)
    for i, (_, text) in enumerate(possible, 1):
        print("    %d  %s" % (i, text))
    api_key = [k for k, _ in possible]

    def write_out(label, choice):
        """Show the visible text rather than the internal key."""
        for i, (k, text) in enumerate(possible, 1):
            if k == choice:
                print("  %s: %d  %s" % (label, i, text.split("\n")[0]))
                return
        print("  %s: %s" % (label, choice))

    if default_value in api_key:
        write_out(T('Given'), default_value)
        return default_value
    if ASK_SINK is not None:
        choice = ASK_SINK(possible, title)
        write_out(T('Chosen'), choice)
        return choice
    if not sys.stdin.isatty():
        raise RuntimeError(
            T('No input possible. Use %s %s to set what should happen.') % (switch, "|".join(api_key)))
    while True:
        answer = input(T('  Number: ')).strip()
        if answer.isdigit() and 1 <= int(answer) <= len(possible):
            write_out(T('Chosen'), possible[int(answer) - 1][0])
            return possible[int(answer) - 1][0]
        print(T('  Please give a number between 1 and %d.') % len(possible))


def ask_reuse_production(complete, has_result, default_value=None, missing=()):
    """Ask what should happen to the existing production."""
    possible = []
    # Reuse is only offered where everything needed is there: without
    # the statistics there would be no camera cut.
    if has_result and not missing:
        possible.append(("result", T('take the existing result (nothing '
                                     'computed, nothing paid)')))
    if complete:
        possible.append(("rerun", T('recompute with the chosen preset -- '
                                    'the files stay\n       where they are, '
                                    'costs no credit')))
    possible.append(("upload", T('upload everything again and recompute -- '
                                 'this costs credit')))
    possible.append(("abort", T('cancel')))
    return ask_choice(possible, T('What should happen with it?'),
                      T('This production already exists'), default_value)


def rename_tracks(tracks, names, request, new_one):
    """Rename the speakers to the track names used by the production.

    Matching goes by position, and the rename applies everywhere: to the
    tracks -- which drive file names, statistics and camera assignment --
    and to the request sent to Auphonic.
    """
    for track, old, fresh in zip(tracks, list(names), new_one):
        print("    %-22s -> %s" % (old, fresh))
        track["name"] = fresh
    names[:] = list(new_one)
    for entry, fresh in zip(request.get("multi_input_files") or [], new_one):
        entry["id"] = fresh


def ask_track_names(old, fresh, default_value=None):
    """Ask what to do when the production uses different track names."""
    print(T('\n  The tracks are named differently there:'))
    for i, name in enumerate(fresh, 1):
        print(T('    Track %d  %-22s (here: %s)')
              % (i, name, old[i - 1] if i <= len(old) else "--"))
    if len(old) != len(fresh):
        print(T('  There are %s tracks there and %s here -- that does not '
                'match.') % (group_text(len(fresh)), group_text(len(old))))
        possible = [("upload", T('upload everything again and recompute -- '
                                 'this costs credit')),
                    ("abort", T('cancel'))]
    else:
        possible = [("adopt", T('take the names from there and carry on '
                                'with them --\n       no upload, costs '
                                'nothing')),
                    ("upload", T('keep our names and upload everything '
                                 'again -- this costs\n       credit')),
                    ("abort", T('cancel'))]
    return ask_choice(possible, T('What should happen with it?'),
                      T('Different track names'), default_value)


def reuse_production(key, existing, request, preset, tracks,
                               names, target_folder, base, wait_s, carry_on):
    """Reuse a production that already exists.

    Only the upload costs credit, not the computation. Trying different
    presets therefore means leaving the files in place and recomputing.
    """
    print(T('\n  THERE IS ALREADY A PRODUCTION WITH THIS NAME'))
    complete, has_result, missing = print_production(existing)
    # "reuse" answers the second question; for the first it means
    # "recompute, upload nothing".
    choice = ask_reuse_production(complete, has_result,
                            "rerun" if carry_on == "adopt" else carry_on,
                            missing)
    uuid = existing.get("uuid")
    if choice == "abort":
        raise RuntimeError(
            T('Stopped. Choose another production name -- then a new '
              'production\n  is created -- or pick one of the other options.'))

    if choice == "rerun" and not complete:
        raise RuntimeError(
            T('Files are missing there -- without a new upload nothing can '
              'be computed.\n  With --auphonic-resume upload the script '
              'uploads again; this costs credit.'))
    upload_again = (choice == "upload")
    if not upload_again:
        # There the tracks are named as they were on upload, the result files
        # in the ZIP are named after that, and Auphonic matches the files
        # through it. Where the names differ we either adopt theirs, which
        # costs nothing, or upload again. We never upload unasked.
        there = [x.get("id") for x in
                (existing.get("multi_input_files") or [])]
        if sorted(there) != sorted(names):
            second = ask_track_names(list(names), there, carry_on)
            if second == "abort":
                raise RuntimeError(
                    T('Stopped. Nothing was uploaded and nothing computed.'))
            if second == "adopt":
                print(T('  The names from there are adopted:'))
                rename_tracks(tracks, names, request, there)
            else:
                upload_again = True
                choice = "upload"

    if choice == "result":
        if not has_result:
            raise RuntimeError(T('This production has no result yet.'))
        if missing:
            raise RuntimeError(
                T('The existing result is unusable: %s is missing there. '
                  'With --auphonic-resume rerun it can be recomputed '
                  'without uploading anything.') % T(' and ').join(missing))
        print(T('  Existing result adopted -- nothing computed, nothing paid.'))
        p = (_parse_json(_curl_call(key, [AUPHONIC + "/api/production/%s.json" % uuid]))
             .get("data") or {})
        return download_results(key, p, names, target_folder, base)

    if not upload_again:
        print(T('  Note: this computes with the files uploaded at the '
                'time. They carry\n  the time window and the alignment of '
                'that day. Where the In point, the Out point\n  or the '
                'measured '
                'position differ now, the return check measures the\n  '
                'difference and moves the tracks into place.'))
    print(T('  Settings brought to preset %r')
          % (preset.get("preset_name") or "?"))
    change = dict(request)
    if not upload_again:
        # The track list stays out here. Auphonic appends it on update instead
        # of matching it -- three tracks became six, the second three without
        # a file. The tracks follow individually in a moment, each through its
        # own URL; only that way are they matched.
        change.pop("multi_input_files", None)
        change.pop("is_multitrack", None)
        # The same goes for the output files: what is already there must not
        # come along again, or Auphonic computes it twice.
        absent_ones = missing_outputs(existing.get("output_files"),
                                     request.get("output_files") or [])
        if absent_ones:
            change["output_files"] = absent_ones
            print(T('  Added: %s')
                  % ", ".join(str(e.get("format")) for e in absent_ones))
        else:
            change.pop("output_files", None)
            print(T('  All needed output files already exist.'))
        left_over = [t.get("id") for t in (existing.get("multi_input_files")
                                        or []) if t.get("id") not in names]
        if left_over:
            print(as_warn(T('  Caution: the production holds further '
                            'tracks (%s). They go into the\n  mix -- please '
                            'delete them at auphonic.com.') % ", ".join(str(u) for u in left_over)))
    update_production(key, uuid, change)
    if not upload_again:
        # The track list could not go above, since the production appends it.
        # Each track through its own URL does work.
        changed, same, bad = update_all_tracks(
            key, uuid, request.get("multi_input_files") or [], existing)
        parts = []
        if changed:
            parts.append(T('%s brought to the preset')
                         % group_text(len(changed)))
        if same:
            parts.append(T('%s were already right') % group_text(len(same)))
        print(T('  Tracks: %s') % (", ".join(parts) or T('nothing to do')))
        for line in bad:
            print(as_warn(T('  Caution: track %s -- it keeps its settings.') % line))
        after = read_production(key, uuid)
        now = after.get("multi_input_files") or []
        if len(now) > len(existing.get("multi_input_files") or []):
            raise RuntimeError(
                T('Tracks were added while changing (now %s). That makes '
                  'the mix\n  wrong. Please delete the tracks without a '
                  'file at auphonic.com.') % group_text(len(now)))
    if upload_again:
        print(T('  The files are uploaded again -- this costs credit.'))
        upload_args = ["-X", "POST",
                AUPHONIC + "/api/production/%s/upload.json" % uuid]
        for track in tracks:
            upload_args += ["-F", "%s=@%s" % (track["name"], track["axis"])]
        d = _parse_json(_curl_call(key, upload_args,
                        progress=T('Uploading %s tracks')
                        % group_text(len(tracks))))
        absent = [x.get("id") for x in ((d.get("data") or {}).get(
            "multi_input_files") or []) if not x.get("input_file")]
        if absent:
            raise RuntimeError(T('These tracks got no file: %s')
                               % ", ".join(absent))
    else:
        print(T('  The existing files are reused -- recomputing costs nothing.'))
    _curl_call(key, ["-X", "POST",
                AUPHONIC + "/api/production/%s/start.json" % uuid])
    p = wait_for_production(key, uuid, wait_s)
    return download_results(key, p, names, target_folder, base)


def wait_for_production(key, uuid, wait_s):
    """Wait for the production to finish, with a progress bar and a timeout."""
    started = time.time()
    end = started + wait_s
    horizon = 150.0
    print(T('  Time limit: %s') % as_hms(wait_s))
    while time.time() < end:
        d = _parse_json(_curl_call(key, [AUPHONIC + "/api/production/%s.json" % uuid]))
        p = d.get("data") or {}
        status, text = p.get("status"), p.get("status_string") or "?"
        if status == 3:
            sys.stdout.write(T('\r  [%-30s] 100 %%  %s  done%s\n')
                             % ("#" * 30, as_hms(time.time() - started), " " * 20))
            return p
        if status == 2:
            raise RuntimeError(T('Auphonic reports an error: %s')
                               % (p.get("error_message") or text))
        for _ in range(5):
            elapsed = time.time() - started
            while elapsed >= horizon:
                horizon *= 2
            share = min(0.99, elapsed / horizon)
            sys.stdout.write("\r  [%-30s] %3.0f %%  %s  %s        "
                             % ("#" * int(share * 30), share * 100,
                                as_hms(elapsed), text))
            sys.stdout.flush()
            if time.time() >= end:
                break
            time.sleep(2)
    raise RuntimeError(T('Time limit of %s reached, production still '
                         'running: %s/engine/status/%s') % (as_hms(wait_s), AUPHONIC, uuid))


def tracks_folder(folder, create=True):
    """Return the folder with the tracks and everything else from Auphonic."""
    target = os.path.join(folder, "auphonic-tracks")
    if create:
        os.makedirs(target, exist_ok=True)
    return target


def match_zip_entries_to_tracks(zip_file_path, names, target_folder):
    """Unpack the ZIP and match its files to the track names.

    Auphonic does not guarantee how it names the files in the ZIP, so no
    name is assumed; the closest match is used.
    """
    import zipfile
    folder = tracks_folder(target_folder)
    with zipfile.ZipFile(zip_file_path) as zf:
        files = [n for n in zf.namelist()
                   if not n.endswith("/") and not os.path.basename(n).startswith(".")]
        zf.extractall(folder)
    assignment, pending = {}, list(files)
    print(T('  In the archive: %s') % ", ".join(os.path.basename(d) for d in files))
    try:
        # Once unpacked the ZIP is no longer needed.
        os.unlink(zip_file_path)
    except OSError:
        pass
    # What the entries do not have in common. Where each carries the
    # episode title and the title carries the speakers' names, the
    # whole name tells them apart worse than nothing: "Guest" scored
    # 0.286 against the Host entry and 0.278 against its own.
    stems = [os.path.splitext(os.path.basename(d))[0] for d in files]
    head = os.path.commonprefix(stems) if len(stems) > 1 else ""
    tail = (os.path.commonprefix([x[::-1] for x in stems])[::-1]
            if len(stems) > 1 else "")
    telling = {d: (x[len(head):len(x) - len(tail)] or x)
               for d, x in zip(files, stems)}

    for name in names:
        if not pending:
            break
        best = max(pending, key=lambda d: similarity(name, telling[d]))
        quality = similarity(name, telling[best])
        if name.lower() in telling[best].lower() or quality > 0.4:
            assignment[name] = os.path.join(folder, best)
            pending.remove(best)
            print("    %-20s <- %s" % (name, os.path.basename(best)))
        else:
            print(T('    %-20s <- nothing suitable found') % name)
    return assignment


# What a camera carries beyond the time window at each end. The run's
# own cross-check calls an offset wrong past a single frame, so a second
# is more than twenty times the error it tolerates -- and at the front
# the key frame the copy has to start on usually swallows it anyway.
CAMERA_MARGIN_S = 1.0


def key_frame_at_or_before(video, when):
    """Where the last key frame at or before *when* seconds sits.

    A stream copy that starts between two key frames takes the picture
    from the key frame before it while the sound starts where it was
    asked, and the two then sit up to one group of pictures apart. So
    the cut goes back to a key frame, never forward. Nothing found means
    0.0, which cuts nothing off the front.
    """
    if when <= 0:
        return 0.0
    for reach in (10.0, 120.0, 1200.0):
        begin = max(0.0, when - reach)
        try:
            p = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0",
                 "-skip_frame", "nokey", "-show_entries", "frame=pts_time",
                 "-of", "csv=p=0", "-read_intervals",
                 "%.3f%%%.3f" % (begin, when + 0.001), video],
                capture_output=True, timeout=300)
        except Exception as e:
            print(T('  Key frames of %s cannot be read (%s) -- the copy '
                    'starts at the beginning of the file.')
                  % (os.path.basename(video), str(e)[:60]))
            return 0.0
        found = []
        for line in p.stdout.decode("utf-8", "replace").splitlines():
            try:
                seconds = float(line.strip().rstrip(","))
            except ValueError:
                continue
            if seconds <= when + 1e-6:
                found.append(seconds)
        if found:
            return max(found)
        if begin <= 0:
            break
    return 0.0


def camera_window_cut(video, duration, offset, window_s):
    """Which stretch of a camera a time window leaves: (cut_at, keep_s).

    *offset* is where the camera's first frame sits in programme time.
    The copy starts on the key frame before the window, so the picture
    is not taken from between two of them; the end is cut wherever the
    window ends, whether or not that key frame could be found. keep_s is
    None where neither end has anything to give up.
    """
    first = max(0.0, -offset - CAMERA_MARGIN_S)
    last = min(duration, window_s - offset + CAMERA_MARGIN_S)
    cut_at = key_frame_at_or_before(video, first)
    if cut_at <= 0 and last >= duration - 0.001:
        return 0.0, None
    return cut_at, max(1.0, last - cut_at)


def camera_stamp(info, cut_at, at_s):
    """The timecode a written camera file carries, or nothing.

    *at_s* is where its first frame sits on the wall clock, out of the
    measurement -- the same reckoning every camera gets, so they agree
    with each other. Written at this camera's own rate. Without it, the
    camera's own timecode moved by what was cut off the front is what
    is left, and then each stands on its own clock again.
    """
    fps = max(1.0, info.get("fps") or 30.0)
    if at_s is not None:
        return timecode_string(at_s, fps)
    return timecode_moved(info["tc"], cut_at, fps) if info.get("tc") else ""


def write_camera_file(video, info, audio_tracks, target, a, b, drift, args,
                 head_s=0, tail_s=0, cut_at=0.0, keep_s=None, at_s=None):
    """Write a new video file carrying several audio tracks.

    *audio_tracks* is a list of (name, path). They all sit on the same
    axis and get the same offset and clock correction, so they stay as
    precisely aligned to each other as they were. *head_s* and *tail_s*
    trim samples from the front and back before the offset is applied.
    *cut_at* and *keep_s* say which stretch of the camera is written;
    *a* then counts from there, and the timecode moves with it.
    """
    kept = keep_s if keep_s else info["duration"] - cut_at
    n_video = int(round(kept * SR))
    if drift and abs(b - 1.0) > 1e-7:
        intro = rate_filter_chain(b) + ","
        k = int(round(a / b * SR))
    else:
        intro, k = "", int(round(a * SR))
    cut = ("atrim=start_sample=%d,asetpts=N/SR/TB," % k) if k > 0 else\
              ("adelay=delays=%dS:all=1," % (-k)) if k < 0 else ""
    cmd = ["ffmpeg", "-v", "warning", "-nostats"]
    # Both in front of the input, so they cut the camera alone: the
    # tracks that follow are inputs of their own and keep their length.
    if cut_at > 0:
        cmd += ["-ss", "%.6f" % cut_at]
    if keep_s:
        cmd += ["-t", "%.6f" % keep_s]
    cmd += ["-i", video]
    chains, map_args = [], ["-map", "0:v"]
    for i, (_, file_path) in enumerate(audio_tracks):
        cmd += ["-i", file_path]
        edge = ""
        if head_s or tail_s:
            edge = ("atrim=start_sample=%d:end_sample=%d,asetpts=N/SR/TB,"
                    % (head_s, sample_count(file_path) - tail_s))
        chains.append("[%d:a]%s%s%sapad=whole_len=%d,atrim=end_sample=%d,"
                      "asetpts=N/SR/TB[t%d]"
                      % (i + 1, edge, intro, cut, n_video, n_video, i))
        map_args += ["-map", "[t%d]" % i]
    n_camera = 0
    if not args.no_camera_audio:
        for i in range(len(info["audio"])):
            map_args += ["-map", "0:a:%d" % i]
        n_camera = len(info["audio"])
    # Behind the audio, so every track above keeps the place the rest of
    # the program counts on.
    data_maps = data_track_maps(video)
    map_args += data_maps
    cmd += ["-filter_complex", ";".join(chains)] + map_args
    if data_maps:
        cmd += ["-c:d", "copy"]
    # use_metadata_tags: keep the camera's QuickTime keys -- Resolve
    #                    reads device and input colour space from them.
    # No write_colr: a colr box that is there travels either way, and
    # where there is none the switch invents 2/2/2, "unspecified".
    cmd += ["-c:v", "copy"] + colour_arguments(video)
    cmd += ["-map_metadata", "0", "-movflags", "+use_metadata_tags"]
    for i in range(len(audio_tracks)):
        cmd += ["-c:a:%d" % i, "pcm_s24le"]
    for i in range(n_camera):
        cmd += ["-c:a:%d" % (len(audio_tracks) + i), "copy"]
    for i, (name, _) in enumerate(audio_tracks):
        cmd += ["-metadata:s:a:%d" % i, "title=%s" % name,
                "-metadata:s:a:%d" % i, "handler_name=%s" % name,
                "-disposition:a:%d" % i, "default" if i == 0 else "0"]
        if args.speech_language:
            cmd += ["-metadata:s:a:%d" % i, "language=%s" % args.speech_language]
    for i in range(n_camera):
        nm = args.name_camera if n_camera == 1 else "%s %d" % (args.name_camera,
                                                               i + 1)
        j = len(audio_tracks) + i
        cmd += ["-metadata:s:a:%d" % j, "title=%s" % nm,
                "-metadata:s:a:%d" % j, "handler_name=%s" % nm,
                "-disposition:a:%d" % j, "0"]
        if args.speech_language_camera:
            cmd += ["-metadata:s:a:%d" % j, "language=%s" % args.speech_language_camera]
    stamp = camera_stamp(info, cut_at, at_s)
    if stamp:
        # ffmpeg carries the source timecode through unchanged however
        # much is cut off the front, so the moment this file really
        # begins has to be written here. Whoever plays it reads the
        # camera's place off that.
        cmd += ["-timecode", stamp]
    cmd += ["-y", target]
    run_ffmpeg_with_progress(cmd, kept,
                              T('Writing %s') % os.path.basename(target))


def measure_loudness(file_path, duration=None, text_progress_bar=None):
    """Measure programme loudness and true peak to EBU R128."""
    cmd = ["ffmpeg", "-nostats", "-i", file_path, "-af", "ebur128=peak=true",
           "-f", "null", "-"]
    if not text_progress_bar:
        p = subprocess.run(cmd, capture_output=True)
        text = p.stderr.decode("utf-8", "replace")
    else:
        # ebur128 writes one line per second to stderr. Reading stdout line by
        # line and stderr only afterwards fills its buffer and both wait for
        # each other, so stderr goes to a file rather than a pipe.
        cmd = cmd[:1] + ["-progress", "pipe:1"] + cmd[1:]
        fd, log = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            with open(log, "wb") as f:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=f)
                show_progress(text_progress_bar, 0.0)
                for line in proc.stdout:
                    share = progress_from_line(line, duration)
                    if share is not None:
                        show_progress(text_progress_bar, share)
                proc.wait()
            with open(log, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        finally:
            try:
                os.unlink(log)
            except OSError:
                pass
        show_progress(text_progress_bar, 1.0)
        if OUTPUT_SINK:
            OUTPUT_SINK("\n")
        else:
            sys.stdout.write("\n")
    def get(label):
        hit = re.findall(label + r":\s*(-?\d+(?:\.\d+)?)", text)
        return float(hit[-1]) if hit else None
    # LRA comes from the same pass: the loudness range says how far quiet and
    # loud passages lie apart. For speech 3 to 7 LU is usual; below that it
    # sounds squashed.
    return get(r"I"), get(r"Peak"), get(r"LRA")


def remove_slow_level_drift(env, window=600):
    """Remove slow level changes from an envelope.

    A leveler changes loudness over time, so envelopes from before and
    after look like different signals even though the onsets sit in the
    same places. Subtracting the moving average leaves the onsets and
    drops the level shaping.
    """
    if len(env) < window * 2:
        return env
    kernel = np.ones(window) / window
    return env - np.convolve(env, kernel, mode="same")


def refine_offset(axis, done, a, b, rate=16000, how_many=9):
    """Measure the remaining offset between upload and returned file.

    Envelopes on a 5 ms grid get no closer than a few milliseconds; here
    the same voice is compared directly in both files. Where to measure
    is decided by level -- the runtime is split into sections and the
    loudest second of each used, since somebody speaking rarely is
    silent at almost any fixed spot. Returns milliseconds, or None.
    """
    try:
        coarse = np.asarray(decode_audio(axis, rate=4000), dtype=np.float64)
    except Exception:
        return None
    nb = 4000
    count = len(coarse) // nb
    if count < how_many:
        return None
    level = np.array([float(np.sqrt((coarse[k * nb:(k + 1) * nb] ** 2).mean()))
                      for k in range(count)])
    loud = float(np.percentile(level[level > 0], 90)) if (level > 0).any() \
        else 0.0
    if loud <= 0:
        return None
    spots = []
    for k in range(how_many):
        begins, until = count * k // how_many, count * (k + 1) // how_many
        if until <= begins:
            continue
        best = begins + int(np.argmax(level[begins:until]))
        if level[best] > loud * 0.3:
            spots.append(best)
    values = []
    for t in spots:
        try:
            x = decode_audio(axis, rate=rate, ss=max(0.0, t - 0.5), duration=2.0)
            y = decode_audio(done, rate=rate,
                           duration=2.0, ss=max(0.0, a + b * (t - 0.5)))
        except Exception:
            continue
        n = min(len(x), len(y))
        if n < rate:
            continue
        x = np.asarray(x[:n], dtype=np.float64)
        y = np.asarray(y[:n], dtype=np.float64)
        ms, sharpness = gcc_phat_offset(x, y, rate)
        if sharpness >= 10:
            values.append(ms)
    if len(values) < 3:
        return None
    return float(np.median(values))


def verify_returned_tracks(tracks, window_length2, tmpdir):   # noqa: C901
    """Check what Auphonic returns against what was uploaded.

    The service can prepend material and change the length; either would
    shift the tracks against each other and undo the alignment.
    De-bleeding removes the other speakers and the leveler bends the
    levels, so the sample points are picked on the processed track, the
    envelopes flattened, and the estimate a median, not a regression.
    """
    print(as_head(T('\nCHECK THE RETURN')))
    HOP, rate = 5.0, 4000
    shaky = []
    # A stereo track that comes back with one channel has been folded at
    # auphonic.com, and no later step can undo that. It is not an error --
    # the run carries on -- but it has to be said, because the difference
    # between the two microphones is then gone from the mix.
    folded = [track["name"] for track in tracks
              if track.get("done") and kept_channels(track["axis"]) == 2
              and kept_channels(track["done"]) == 1]
    if folded:
        print(as_warn(TN(len(folded),
                         '  %s went up in stereo and came back in one '
                         'channel.',
                         '  %s went up in stereo and came back in one '
                         'channel each.') % ", ".join(folded)))
        print(T('  auphonic.com folded them. The mix keeps the two '
                'channels; what is gone is the\n  difference between the '
                'two microphones of that track.'))
    for track in tracks:
        done = track.get("done")
        if not done:
            continue
        n_fresh = sample_count(done) / float(SR)
        try:
            env_old = remove_slow_level_drift(envelope(decode_audio(track["axis"], rate=rate),
                                         HOP, rate))
            env_fresh = remove_slow_level_drift(envelope(decode_audio(done, rate=rate),
                                         HOP, rate))
            # Pick the sample points on the processed track, not the
            # uploaded one: after de-bleeding only one speaker is left,
            # and one comparison over the whole length would be
            # dominated by the passages where the track is now empty.
            density = int(max(20, min(120, len(env_fresh) * HOP / 1000.0 / 30.0)))
            a_corr, b_corr, st = align_envelopes(env_old, env_fresh, HOP,
                                                sample_points=density,
                                                distance_s=30.0,
                                                warn=os.path.basename(done),
                                                points_off="audio")
        except Exception as e:
            print(T('  %-20s not measurable: %s') % (track["name"], e))
            if track.get("edge"):
                # Without a measurement only the computed edge is left.
                target = os.path.join(tmpdir,
                                    "ready_%s.wav" % safe_filename(track["name"]))
                track["ready"] = place_track_on_axis(done, target, track["edge"], 1.0,
                                              0.0, window_length2, drift=False)
            else:
                track["ready"] = done
            continue
        # Median rather than a regression line: Auphonic shifts a track as a
        # whole or not at all, so there is no slope to estimate here.
        offsets = st.get("offsets") or []
        times = st.get("times") or []
        clock_drift, clock_drift_ppm = 1.0, 0.0
        if offsets:
            v = np.array(offsets)
            a_corr = -float(np.median(v))
            spread = float(np.median(np.abs(v - np.median(v))) * 1000)
            # A returned file drifting against the uploaded one carries
            # clock drift -- an older production reused whose tracks came
            # from a run with a different correction. A fixed offset is
            # then not enough and the crossing voice becomes audible.
            if len(v) >= 20 and len(times) == len(v):
                t = np.array(times)
                slope, axis = np.polyfit(t, v, 1)
                rest = v - (axis + slope * t)
                if (abs(slope) * 1e6 > 2.0
                        and float(np.std(rest) * 1000) < 30.0):
                    clock_drift = 1.0 / (1.0 + slope)
                    clock_drift_ppm = (clock_drift - 1.0) * 1e6
                    a_corr = -axis / (1.0 + slope)
                    spread = float(np.median(np.abs(rest)) * 1000)
        else:
            spread = st.get("spread_ms", 0.0)
        # Where the file was coarsely trimmed to a window set later,
        # there is deliberate slack at both ends and the offset should be
        # exactly that. Measured on the voice rather than the envelope:
        # between tracks, a second voice becomes audible from about 20 ms.
        fine = refine_offset(track["axis"], done, a_corr, clock_drift)
        if fine is not None and abs(fine) < 500.0:
            a_corr += fine / 1000.0
        edge = track.get("edge", 0.0)
        ms = (a_corr - edge) * 1000.0
        # Record what was measured here for the metrics.
        track["drift_ppm"] = clock_drift_ppm
        track["offset_ms"] = ms
        track["residual_ms"] = spread
        length = n_fresh - 2 * edge - window_length2
        remark = ""
        if edge or abs(ms) > 5 or abs(length) > 0.05 or clock_drift_ppm:
            target = os.path.join(tmpdir, "ready_%s.wav" % safe_filename(track["name"]))
            place_track_on_axis(done, target, a_corr, clock_drift, 0.0, window_length2,
                           drift=bool(clock_drift_ppm))
            track["ready"] = target
            remark = (T('  -->  aligned, clock drift %s ppm taken out')
                      % decimal_text("%+.1f" % clock_drift_ppm)) \
                if clock_drift_ppm \
                else T('  -->  aligned')
        else:
            track["ready"] = done
        uncertain = st.get("points", 0) < 5 or spread > 150.0
        line = (T('  %-20s offset %s ms%s, length %s s, spread %s '
                  'ms, %s of %s points%s%s')
                % (track["name"], decimal_text("%+.1f" % ms),
                   "" if fine is None else T(' (fine: %s ms)')
                   % decimal_text("%+.1f" % fine),
                   decimal_text("%+.3f" % length),
                   decimal_text("%.0f" % spread),
                   group_text(st.get("points", 0)),
                   group_text(st.get("candidates", 0)), remark,
                   T('   Caution: measurement unusable') if uncertain else ""))
        print(as_warn(line) if uncertain else line)
        if uncertain:
            shaky.append(track["name"])
    if shaky:
        print(T('\n  For %s it could not be established whether the return '
                'matches the\n  upload. Better to stop than to write '
                'something wrong.') % ", ".join(shaky))
        return False
    return True


def find_master_file(*places):
    """Find the finished mixdown from auphonic.com, if it came along."""
    for place in places:
        if not place:
            continue
        for folder in (tracks_folder(place, create=False), place):
            try:
                names = sorted(os.listdir(folder))
            except OSError:
                continue
            for n in names:
                small = n.lower()
                if ("master" in small and small.endswith(".wav")
                        and not small.startswith("final_")):
                    return os.path.join(folder, n)
    return None


def remove_quietly(path):
    """Delete a working file. Returns whether it went.

    The measuring sum is several hundred megabytes and the run carries
    on long after it. A file already gone is not a fault, but the answer
    is handed back rather than swallowed, for a caller that does care.
    """
    try:
        os.unlink(path)
    except OSError:
        return False
    return True


def normalise_loudness(tracks, target_lufs, tmpdir, master=None, channels=1):
    """Compute one common gain for all tracks.

    The sum is measured, not the single track, because only the sum is
    heard; the same gain goes on every track so the speakers keep the
    balance Auphonic set. Where the finished mixdown is present it is
    the yardstick. *target_lufs* None means adjust nothing -- the sum is
    still measured, or an omitted adjustment looks like a fault later.
    """
    print(as_head(T('\nNORMALISE')))
    keep = target_lufs is None
    after_yardstick = False
    if master and os.path.exists(master) and not keep:
        m_have, m_peak, _m_lra = measure_loudness(master, None, T('Measuring the '
                                                                  'yardstick'))
        if m_have is not None:
            after_yardstick = True
            print(T('  Mixdown from auphonic.com: %s LUFS, peak %s '
                    'dBTP (%s)')
                  % (decimal_text("%.1f" % m_have),
                     decimal_text("%.1f" % (m_peak if m_peak is not None
                                            else 0.0)),
                     os.path.basename(master)))
            target_lufs = m_have
    total_sum = os.path.join(tmpdir, "measure_sum.wav")
    ready = [track["ready"] for track in tracks]
    # Measured in the form it is delivered in: a two channel mix sits a good
    # three decibels above the same mix as one track. A stereo track raises
    # the count on its own -- the mix it goes into has two channels, so the
    # measurement has to have them too.
    channels = max(channels, widest_track(ready))
    parts, chains, markers = [], [], []
    for i, path in enumerate(ready):
        parts += ["-i", path]
        chains.append("[%d:a]%s[m%d]"
                      % (i, channel_filter(kept_channels(path), channels), i))
        markers.append("[m%d]" % i)
    fc = ";".join(chains) + ";" + "".join(markers) +\
        "amix=inputs=%d:normalize=0[out]" % len(markers)
    duration = sample_count(tracks[0]["ready"]) / float(SR)
    # One track with nothing to do to its channels is its own sum, and
    # summing it anyway copies hours of audio to arrive at the same
    # samples. *ours* says whether this run made that file: only a file
    # of our own may be deleted by the clean-ups further down.
    ours = not (len(ready) == 1 and "anull" in chains[0])
    measured_on = total_sum if ours else ready[0]
    if ours:
        run_ffmpeg_with_progress(
            ["ffmpeg", "-v", "error"] + parts + ["-filter_complex", fc,
             "-map", "[out]", "-c:a", "pcm_s24le"]
                + wav_safe(total_sum) + ["-y", total_sum],
            duration, T('Building the sum'))
    have, peak, lra_range = measure_loudness(measured_on, duration,
                                            T('Measuring loudness'))
    if have is None:
        print(T('  Loudness not measurable -- it stays as it is.'))
        return 0.0, None
    if keep:
        print(T('  Sum of tracks:     %s LUFS, peak %s dBTP%s')
              % (decimal_text("%.1f" % have),
                 decimal_text("%.1f" % (peak if peak is not None else 0.0)),
                 T(', range %s LU') % decimal_text("%.1f" % lra_range)
                 if lra_range is not None else ""))
        print(T('  Not adjusted:      taken from the source files -- no gain '
                'on any track and no\n                     limiter. The '
                'sound leaves exactly as it came in.'))
        if ours:
            remove_quietly(total_sum)
        return 0.0, None
    gain = target_lufs - have
    print(T('  Sum of tracks:     %s LUFS, peak %s dBTP%s')
          % (decimal_text("%.1f" % have),
             decimal_text("%.1f" % (peak if peak is not None else 0.0)),
             T(', range %s LU') % decimal_text("%.1f" % lra_range)
             if lra_range is not None else ""))
    print(T('  Target:            %s LUFS  ->  %s dB on every track')
          % (decimal_text("%.1f" % target_lufs),
             decimal_text("%+.1f" % gain)))
    # Without a ceiling the gain would have to drop far enough for the loudest
    # peak to fit -- a single scraping chair can cost eight decibels. So the
    # gain stays and a limiter catches the peaks.
    if peak is not None and gain > CEILING_DBTP - peak:
        print(T('  Peaks:             %s dB above %s dBTP -- the '
                'limiter catches them')
              % (decimal_text("%+.1f" % (peak + gain - CEILING_DBTP)),
                 decimal_text("%.1f" % CEILING_DBTP)))
    # How much the limiter would have to take off is only known once the curve
    # is computed. Taking off more than a handful of decibels means not that
    # the peak does not fit the target but that the target does not fit the
    # material; then quieter beats squashed.
    curve, gone = limiter_curve(measured_on, tmpdir, gain)
    # With the finished mixdown from auphonic.com beside it the question is
    # answered: that is how much limiting auphonic.com itself needed to reach
    # this loudness from the same tracks, so nothing needs capping.
    limit = 12.0 if after_yardstick else LIMIT_MAX_DB
    if gone > limit + 0.05:
        back = gone - limit
        print(T('  Too much:          the limiter would have to take %s '
                'dB away. More than %s dB\n                     sounds '
                'squashed -- %s dB less gain.')
              % (decimal_text("%.1f" % gone), decimal_text("%.0f" % limit),
                 decimal_text("%.1f" % back)))
        gain -= back
        curve, gone = limiter_curve(measured_on, tmpdir, gain)
        print(T('  Remains:           %s dB on every track, that is '
                '%s LUFS instead of %s')
              % (decimal_text("%+.1f" % gain),
                 decimal_text("%.1f" % (have + gain)),
                 decimal_text("%.1f" % target_lufs)))
    if gone > 0.05:
        print(T('  Limiter:           at most %s dB, the same curve on '
                'every track%s')
              % (decimal_text("%.1f" % gone),
                 T(' (auphonic.com takes the same amount)')
                 if after_yardstick else ""))
    # For checking in the editor. -16 LUFS is the figure for web and podcast;
    # broadcast measures against -23, where the meter reads correspondingly
    # higher.
    print(T('  Result:            about %s LUFS, peak %s dBTP')
          % (decimal_text("%.1f" % (have + gain)),
             decimal_text("%.1f" % (CEILING_DBTP if gone > 0.05
                                    else min(CEILING_DBTP,
                                             (peak or 0.0) + gain)))))
    # The loudness range measures whether any dynamics are left. A limiter that
    # only catches peaks leaves it almost untouched; where it gets small,
    # something was squashed -- and then not by the limiter but by whatever was
    # done before.
    if lra_range is not None:
        if lra_range < 2.0:
            print(as_warn(T('  Caution: range      only %s LU -- very '
                            'tight. Speech is usually 3 to 7 LU;\n          '
                            '           below that it sounds squashed. '
                            'Check how strongly the leveler\n               '
                            '      is set at auphonic.com.')
                          % decimal_text("%.1f" % lra_range)))
        else:
            print(T('  Range:             %s LU (speech is usually 3 to '
                    '7 LU)') % decimal_text("%.1f" % lra_range))
    if ours:
        remove_quietly(total_sum)
    return gain, curve


def limiter_curve(total_sum, tmpdir, gain, ceiling=CEILING_DBTP):
    """Compute the limiter gain curve once, on the sum.

    The same curve goes on every single track, so the tracks add up to
    exactly the mix again: (a+b)*g equals a*g + b*g. A limiter per track
    would follow its own level and clamp the loud one harder. Block by
    block, with one block of lookahead and a linear cross-fade, or it
    clicks; the audio streams. Returns (path, reduction in dB).
    """
    if np is None:
        return None, 0.0
    channels = max(1, channel_count(total_sum))
    limit = 10.0 ** (ceiling / 20.0)
    BLOCK = 256                       # 5.3 ms at 48 kHz
    RECOVERY = math.exp(-BLOCK / (SR * 0.050))    # 50 ms back up
    source = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", total_sum,
         "-af", "volume=%.3fdB" % gain,
         "-f", "f32le", "-ac", str(channels), "-ar", str(SR), "-"],
        stdout=subprocess.PIPE)
    raw = os.path.join(tmpdir, "level_curve.raw")
    target = os.path.join(tmpdir, "level_curve.wav")
    smallest, status, rest, done = 1.0, 1.0, b"", False
    frame_bytes = 4 * channels
    try:
        with open(raw, "wb") as f:
            while not done:
                chunk = source.stdout.read(1 << 20)
                done = not chunk
                data = rest + chunk
                whole_blocks = len(data) // (frame_bytes * BLOCK)
                if not done:
                    # The last block waits for the next chunk: without it there
                    # would be no lookahead there and the peak would come
                    # through a tenth of a second early.
                    whole_blocks = max(0, whole_blocks - 1)
                    full = whole_blocks * frame_bytes * BLOCK
                else:
                    full = len(data) - len(data) % frame_bytes
                rest = data[full:]
                if full <= 0:
                    continue
                frames = np.frombuffer(data[:full],
                                       dtype="<f4").reshape(-1, channels)
                count = int(math.ceil(frames.shape[0] / float(BLOCK)))
                needed = np.ones(count, dtype=np.float64)
                for k in range(count):
                    piece = frames[k * BLOCK:(k + 1) * BLOCK]
                    peak = (float(np.max(np.abs(piece)))
                              if piece.size else 0.0)
                    if peak > limit:
                        needed[k] = limit / peak
                # One block of lookahead: the reduction is in place before the
                # peak.
                before = np.minimum(needed, np.roll(needed, -1))
                before[-1] = needed[-1]
                g = np.empty(frames.shape[0], dtype=np.float32)
                for k in range(count):
                    want = before[k]
                    if want > status:      # back up, but slowly
                        want = min(want, status * RECOVERY + (1.0 - RECOVERY))
                    a0 = k * BLOCK
                    a1 = min(frames.shape[0], a0 + BLOCK)
                    g[a0:a1] = np.linspace(status, want, a1 - a0,
                                           endpoint=False)
                    status = want
                    smallest = min(smallest, want)
                f.write((np.repeat(g, channels) if channels > 1 else g)
                        .astype("<f4").tobytes())
    except Exception as e:
        print(T('  Level curve not possible (%s) -- without limiter') % e)
        return None, 0.0
    finally:
        try:
            source.stdout.close()
            source.wait(timeout=30)
        except Exception:
            pass
    gone = -20.0 * math.log10(max(1e-6, smallest))
    if gone <= 0.001:
        try:
            os.unlink(raw)
        except OSError:
            pass
        return None, 0.0
    try:
        subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le",
                        "-ar", str(SR), "-ac", str(channels), "-i", raw,
                        "-c:a", "pcm_f32le"]
                            + wav_safe(target)
                            + ["-y", target], check=True)
        os.unlink(raw)
    except Exception as e:
        print(T('  Level curve not possible (%s) -- without limiter') % e)
        return None, 0.0
    return target, gone


def channel_count(file_path):
    """Return the channel count of a file."""
    return probe_remember("channels", file_path,
                          lambda: _channel_count(file_path))


def kept_channels(file_path):
    """How many channels a track keeps on its way through: one or two.

    A stereo track is stereo because two microphones stand apart, and
    folding it to one throws that difference away for good. So the rule
    is "keep what the source has". More than two channels is a recorder
    file, not a track; those are cut into tracks before they get here,
    and anything still arriving with more is folded.
    """
    try:
        return 2 if channel_count(file_path) == 2 else 1
    except Exception:
        return 1


def channel_filter(have, want):
    """The filter that brings *have* channels to *want*, without a level jump.

    Both directions are written out rather than left to ffmpeg, whose
    equal-power law lands three decibels out either way -- inaudible in
    a single listen and wrong in every meter. Worse, it depends on the
    output format, so the same call is right in one place and out in the
    next. Here one to two is a copy and two to one a half-and-half sum.
    """
    if have == want:
        return "anull"
    if want == 2:
        return "pan=stereo|c0=c0|c1=c0"
    return "pan=mono|c0=0.5*c0+0.5*c1"


def widest_track(paths):
    """Two if any of these files is stereo, otherwise one."""
    return max([1] + [kept_channels(p) for p in paths])


def _channel_count(file_path):
    try:
        a = next((x for x in ffprobe_json(file_path).get("streams", [])
                  if x.get("codec_type") == "audio"), {})
        return int(a.get("channels") or 1)
    except Exception:
        return 1


def how_many_processors():
    """How many processors this process may actually use.

    os.cpu_count() counts what the machine has, not what this process is
    allowed: held to two of thirty-two, a pool sized by the thirty-two
    means threads taking turns. process_cpu_count arrived in Python
    3.13, so the older one stays as the fallback.
    """
    ask = getattr(os, "process_cpu_count", None) or os.cpu_count
    try:
        return max(1, int(ask() or 2))
    except Exception:
        return 2


def python_note():
    """One line about the Python this is running on, for the log.

    Said rather than assumed: a report that opens with the version it ran
    under saves the first three questions when something behaves oddly.
    """
    now = "%d.%d.%d" % sys.version_info[:3]
    if now == LIKES_PYTHON:
        return "Python %s" % now
    return "Python %s  (recommended version %s)" % (now, LIKES_PYTHON)


def prework_standing(shares):
    """How far the prework has got, and one line per file still at it.

    Every task of a file counts the same, and every file counts the
    same however many tasks it has. What is finished leaves the list:
    the row has served its purpose and the list stays short.
    """
    per_file = {}
    for (path, _task), value in shares.items():
        per_file.setdefault(path, []).append(value)
    got = dict((p, sum(v) / len(v)) for p, v in per_file.items())
    total = sum(got.values()) / len(got)
    lines = ["%s   %3.0f %%" % (os.path.basename(p), 100.0 * got[p])
             for p in sorted(got, key=os.path.basename) if got[p] < 0.999]
    return total, lines


def prework_weight(file_path, task):
    """How much of the bar a piece of prework is worth.

    Pulling the audio out of an hour of 4K and reading a wav file are
    one step each. Equal shares would make the bar say nothing: it would
    stand still through the long one and jump through the short ones.
    """
    video = os.path.splitext(file_path)[1].lower() in VIDEO_SUFFIXES
    if task == "audio":
        return 8.0 if video else 2.0
    if task == "channels":
        return 6.0 if video else 1.5
    if task == "split":
        return 4.0 if video else 2.0
    return 6.0 if video else 1.0


def parallel_map(items, work, workers=None):
    """Run *work* over all *items* at once; answers come back in order.

    Threads rather than processes: everything this is used for waits on
    ffmpeg or numpy, and both let other threads run. Where a thread
    cannot be started the rest is worked through here. An error inside
    the work is raised after all of it is done, so one unreadable file
    does not leave threads running behind a traceback.
    """
    items = list(items)
    if len(items) < 2:
        return [work(x) for x in items]
    if workers is None:
        workers = max(2, min(8, how_many_processors()))
    out = [None] * len(items)
    todo = list(range(len(items)))
    trouble = []

    def work_loop():
        while True:
            if stop_wanted():
                return
            try:
                i = todo.pop()
            except IndexError:
                return
            try:
                out[i] = work(items[i])
            except BaseException as e:      # noqa: BLE001 -- passed on below
                trouble.append(e)

    threads = []
    for _ in range(max(1, min(workers, len(items)))):
        thread = threading.Thread(target=work_loop, daemon=True)
        try:
            thread.start()
        except Exception:
            break
        threads.append(thread)
    for thread in threads:
        try:
            thread.join()
        except Exception:
            pass
    work_loop()             # whatever no thread got to
    if trouble:
        raise trouble[0]
    return out


def probe_warm(paths, workers=None):
    """Ask about several files at once, so the answers are there later.

    Everything the interface needs before it can draw a row is measured
    here in parallel, and the rows are then built from memory. On an
    external volume, asking one after another is the difference between
    a window that stands still for minutes and one that does not.
    """
    todo = [p for p in dict.fromkeys(paths) if p and os.path.exists(p)]
    if len(todo) < 2:
        return

    def one(file_path):
        work = [lambda: ffprobe_json(file_path),
                lambda: channel_count(file_path)]
        if os.path.splitext(file_path)[1].lower() in AUDIO_SUFFIXES:
            work += [lambda: sample_count(file_path),
                     lambda: bext_time_reference(file_path)]
        for task in work:
            try:
                task()
            except Exception:
                # A file that cannot be measured is reported where its
                # row is drawn. Here it must not stop the rest.
                pass

    parallel_map(todo, one, workers)


# A channel counts as silent when it stays this far under the loudest
# channel of the same file. A recorder writes four channels whether or
# not anything was plugged in, and an empty one must not become a
# speaker.
SILENT_BELOW_DB = 45.0
# Absolute floor for a channel that carries anything at all. Under this
# there is only the noise floor of the converter, and a judgement made
# there is comparing dither rather than signal.
QUIET_BELOW_DBFS = -70.0

# Two channels count as the same signal from here up. Mono panned to
# both sides gives exactly 1.0; a hair less allows for lossy coding.
SAME_SIGNAL = 0.999

# How far off zero a shared sound may arrive and still count as coming
# through one pair of microphones. Sound travels 34 cm in a
# millisecond, so this covers every usual stereo spacing and no pair of
# clip-on microphones on two people.
PAIR_DELAY_MS = 1.0

# This much of the strongest common component has to sit inside that
# window for the two channels to be one pair. Every stereo technique
# scores near 1, two clip-ons near 0.1; nothing lands in the middle.
PAIR_AT_ZERO = 0.5

# Two more legs under the same judgement. The share says the two
# channels hear the same thing at the same moment, and in one room
# every microphone does that, so the share alone cannot tell a pair
# from a neighbour. First leg: the spacing measured has to be small.
PAIR_APART_METRES = 0.3
# And it may only be formed where it stands on something. The delay is
# read off the places whose peak missed the zero window; a real spacing
# turns up at nearly every place, so a single one is not enough to
# throw a plain stereo track away.
PAIR_APART_SHARE = 0.25

# Second leg: a pair has to stand out from the two pairs that share a
# channel with it. Pairs running across every pair boundary can score
# as high as the real ones; where nothing stands out, nothing is said.
PAIR_STANDS_OUT = 0.15

# The delay is measured on this many places spread over the file. More
# does not change the figure; on an hour of audio it would only cost
# time while somebody waits for the file list.
PAIR_PLACES = 120

# Below this many usable places the median means nothing, and the row
# says so with the number instead of claiming anything.
PAIR_ENOUGH_PLACES = 8

# Which level counts as "the loud part of this file". The gate below
# hangs on it, so it has to be a level the recording really reaches
# and has to survive a single loud moment. A decile of the places does
# both, where the file's peak would move by tens of decibels.
PAIR_LOUD_PERCENTILE = 90.0

# And the gate sits this far under it. Not a threshold for silence --
# that job belongs to the correlation height further down. What this
# does is hold a recording's own pauses out of the median: much deeper
# and the answer is read from room tone.
PAIR_GATE_UNDER_DB = 20.0


def channel_rate(file_path, channels, want=16000):
    """Pick a working rate that fits the file in memory.

    16 kHz gives the delay measurement a sixteenth of a millisecond,
    which is what it wants; an hour of four channels at that rate is a
    gigabyte, so a long or wide file is read more coarsely. Halving the
    rate halves the resolution.
    """
    try:
        seconds = float(ffprobe_json(file_path).get("format", {})
                        .get("duration") or 0.0)
    except Exception:
        seconds = 0.0
    while want > 4000 and seconds * max(1, channels) * want > 6e8:
        want //= 2
    return want


# Peak level has to be this close to the top before counting starts.
CLIP_NEAR_TOP_DB = -0.1
# How many samples in a row on the stop make one event. One is
# rounding, two is rounding twice; three in a row is a crest the
# converter could not follow, and that is what is heard. It holds for
# speech and music, not for rumble under about 50 Hz.
CLIP_RUN_SAMPLES = 3


def clipping_facts(file_path, stream=0, least=CLIP_RUN_SAMPLES):
    """Count the runs of samples sitting on the stop, per channel.

    Counted here rather than asked of ffmpeg: ``astats`` reports how
    many samples equal the loudest and quietest value *in this file*,
    wherever those lie, so it cannot tell single samples from runs and
    counts files that never reach full scale. Integer formats only --
    float has no stop. Returns {channel: (runs, longest, ms, first s)}.
    """
    if np is None or pcm_kind(file_path, stream) == "pcm_f32le":
        return {}
    try:
        # The stream that was asked about. Reading the rate and the
        # channel count off the first one while the format comes from
        # the nth would count the samples of one stream against the
        # shape of another.
        a = audio_stream_facts(file_path, stream)
        rate = int(a.get("sample_rate") or 0)
        n = int(a.get("channels") or 0)
    except Exception:
        return {}
    if not rate or not n:
        return {}
    return clipping_runs_count(file_path, stream, rate, n, least)


def clipping_runs_count(file_path, stream, rate, n, least):
    """Stream the audio at its own rate and count the runs.

    At the full rate, not the 16 kHz the levels are measured at: a run
    of three samples does not survive resampling. Read block by block,
    because an hour of stereo does not belong in memory at once. Through
    s16le on purpose -- 16 and 24 bit give the same count that way,
    while s32le needs a threshold depending on the original's depth.
    """
    top, bottom, width = 32767, -32768, 2
    try:
        p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-i", file_path,
             "-map", "0:a:%d" % stream, "-c:a", "pcm_s16le",
             "-f", "s16le", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except OSError:
        return {}
    frame = width * n
    want = max(frame, (8 << 20) // frame * frame)
    total = np.zeros(n, dtype=np.int64)
    runs = np.zeros(n, dtype=np.int64)
    longest = np.zeros(n, dtype=np.int64)
    first = np.full(n, -1, dtype=np.int64)
    open_len = np.zeros(n, dtype=np.int64)
    open_at = np.zeros(n, dtype=np.int64)

    def close(k, how_long, where):
        """A run that has ended: count it if it is long enough."""
        if how_long >= least:
            runs[k] += 1
            if first[k] < 0:
                first[k] = where
        if how_long > longest[k]:
            longest[k] = how_long

    rest, base = b"", 0
    try:
        while True:
            raw = p.stdout.read(want)
            if not raw:
                break
            raw = rest + raw
            keep = len(raw) - (len(raw) % frame)
            rest = raw[keep:]
            if not keep:
                continue
            block = np.frombuffer(raw[:keep], dtype=np.int16).reshape(-1, n)
            here = block.shape[0]
            # Two comparisons and not one on the absolute value: int16
            # has no room for the absolute of its own lowest number.
            hit = (block >= top) | (block <= bottom)
            columns = ([int(k) for k in np.flatnonzero(hit.any(axis=0))]
                       if hit.any() else [])
            if columns:
                total += hit.sum(axis=0)
            standing = set(columns)
            for k in np.flatnonzero(open_len):
                k = int(k)
                if k not in standing:
                    close(k, open_len[k], open_at[k])
                    open_len[k] = 0
            for k in columns:
                edge = np.ascontiguousarray(hit[:, k]).view(np.int8)
                step = np.diff(edge, prepend=np.int8(0), append=np.int8(0))
                on = np.flatnonzero(step == 1)
                off = np.flatnonzero(step == -1)
                length = (off - on).astype(np.int64)
                start = base + on.astype(np.int64)
                if open_len[k]:
                    if on[0] == 0:
                        length[0] += open_len[k]
                        start[0] = open_at[k]
                    else:
                        # It ended exactly on the block boundary while
                        # this block has a hit further along. Without
                        # this the run would be dropped: the loop above
                        # skipped the column, and the join does not
                        # apply either.
                        close(k, open_len[k], open_at[k])
                    open_len[k] = 0
                if off[-1] == here:
                    open_len[k] = length[-1]
                    open_at[k] = start[-1]
                    length, start = length[:-1], start[:-1]
                if length.size:
                    longest[k] = max(longest[k], int(length.max()))
                    enough = np.flatnonzero(length >= least)
                    if enough.size:
                        runs[k] += enough.size
                        if first[k] < 0:
                            first[k] = start[enough[0]]
            base += here
    finally:
        # Closed rather than guarded: a pipe being read to its end
        # closes without complaint, and a reader that stopped early
        # would leave ffmpeg writing into a pipe nobody empties.
        p.stdout.close()
        try:
            p.wait(timeout=20)
        except Exception:
            p.kill()
            p.wait()
    if p.returncode:
        # Half a file read is worse than none: the answer would be
        # given on the part that arrived.
        return {}
    for k in range(n):
        if open_len[k]:
            close(k, open_len[k], open_at[k])
    return {k: (int(runs[k]), int(longest[k]),
                float(1000.0 * longest[k] / rate),
                float(first[k]) / float(rate))
            for k in range(n) if runs[k]}


def channel_levels(file_path, rate=16000, stream=0):
    """Return each audio channel of one file on its own.

    One pass through ffmpeg, taken apart here: asking per channel with a
    pan filter decodes the whole file again for every channel. What
    comes out is 32 bit floats whatever the file was, and nothing
    measured here needs more. Empty rows come back where ffmpeg failed,
    since half a file read would be judged as if it were whole.
    """
    n = max(1, channel_count(file_path))
    # One pass, not one per channel: everything comes out interleaved
    # and is taken apart here.
    p = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", file_path,
         "-map", "0:a:%d" % stream, "-ar", str(rate), "-f", "f32le", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    parts = [[] for _ in range(n)]
    rest = b""
    frame = 4 * n
    try:
        while True:
            # A block of whole frames at a time. Reading the lot into one
            # array first would double the memory of a long wide file.
            raw = p.stdout.read(frame * 65536)
            if not raw:
                break
            raw = rest + raw
            keep = len(raw) - (len(raw) % frame)
            rest = raw[keep:]
            if not keep:
                continue
            block = np.frombuffer(raw[:keep], dtype=np.float32).reshape(-1, n)
            for k in range(n):
                parts[k].append(np.ascontiguousarray(block[:, k]))
    finally:
        try:
            p.stdout.close()
        except OSError:
            pass
        # A reader that stopped early leaves ffmpeg writing into a pipe
        # nobody empties, and it would sit there for ever.
        try:
            p.wait(timeout=20)
        except Exception:
            p.kill()
            p.wait()
    if p.returncode:
        # Half a file read is worse than none: the judgement would be
        # made on the part that arrived and then stored under the file's
        # size and time, so it would never be measured again.
        return [np.zeros(0, dtype=np.float32) for _ in range(n)]
    # Joined one channel at a time, and each list of pieces dropped as
    # soon as it has been joined. Building them all first would hold the
    # whole recording twice -- which is what the chunked read is for.
    out = []
    for k in range(n):
        out.append(np.concatenate(parts[k]) if parts[k]
                   else np.zeros(0, dtype=np.float32))
        parts[k] = None
    return out


def channel_at_zero(first, second, rate, most=PAIR_PLACES, window=2048):
    """How much of what two channels share arrives at the same time.

    One pair of microphones hears everything at nearly the same moment;
    two on two people hear each other late. So the question is not how
    alike the channels are but *when* what they share arrives. Returns
    (share, places, apart, agreed). Plain correlation, not PHAT, which
    turns the silences speech leaves in both channels into a spike.
    """
    # Both legs come off the same places, and only one off all of them:
    # the share is the median over every usable place, the distance
    # only over those whose peak missed the window -- see pair_spacing.
    width = min(len(first), len(second))
    if width < window * 2:
        return 0.0, 0, 0.0, 0
    reach = max(4, int(0.020 * rate))
    close = max(1, int(PAIR_DELAY_MS * rate / 1000.0))
    spots = np.linspace(0, width - window - 1, most).astype(int)
    # How loud each place is, all of them before any is judged: the gate
    # is a level of this file and cannot be known one place at a time.
    # A peak is not a level, which is why the gate hangs on the places
    # and not on the loudest sample.
    strong = np.zeros(len(spots))
    for j, i in enumerate(spots):
        a = first[i:i + window].astype(np.float64)
        b = second[i:i + window].astype(np.float64)
        strong[j] = max(math.sqrt(float((a ** 2).mean())),
                        math.sqrt(float((b ** 2).mean())))
    loud = float(np.percentile(strong, PAIR_LOUD_PERCENTILE))
    if loud <= 0:
        return 0.0, 0, 0.0, 0
    gate = loud * 10 ** (-PAIR_GATE_UNDER_DB / 20.0)
    n = 1 << int(math.ceil(math.log(window * 2, 2)))
    # Below this the two channels share nothing worth reading a delay
    # out of, and the highest point of the correlation is wherever the
    # noise happens to be tallest.
    shared_enough = 0.10
    out, away = [], []
    for j, i in enumerate(spots):
        if strong[j] < gate:
            continue
        a = first[i:i + window]
        b = second[i:i + window]
        a = a.astype(np.float64) - float(a.mean())
        b = b.astype(np.float64) - float(b.mean())
        size = math.sqrt(float((a ** 2).sum()) * float((b ** 2).sum()))
        if size <= 0:
            continue
        cc = np.fft.irfft(np.fft.rfft(a, n) * np.conj(np.fft.rfft(b, n)), n)
        band = np.abs(np.concatenate((cc[-reach:], cc[:reach + 1]))) / size
        highest = float(band.max())
        if highest < shared_enough:
            continue
        out.append(float(band[reach - close:reach + close + 1].max())
                   / highest)
        where = int(np.argmax(band)) - reach
        if abs(where) > close:
            away.append(abs(where) * 1000.0 / float(rate))
    if len(out) < PAIR_ENOUGH_PLACES:
        return 0.0, len(out), 0.0, 0
    apart, agreed = pair_spacing(away, len(out))
    return float(np.median(out)), len(out), apart, agreed


def pair_spacing(away, places=0):
    """The one delay the late arrivals agree on, and how many agree.

    *away* is how late the strongest shared sound was where it missed
    the zero window. A spacing is a fixed length of air and turns up as
    the same delay again and again; where the delays scatter there is
    none, only a correlation wandering about a room. So the median
    counts only if most agree within one window, and over enough places.
    """
    if not away or len(away) < PAIR_APART_SHARE * max(0, places):
        return 0.0, 0
    middle = float(np.median(away))
    near = [x for x in away if abs(x - middle) <= PAIR_DELAY_MS / 2.0]
    if len(near) * 2 > len(away):
        return middle, len(near)
    return 0.0, 0


def channel_hush(level):
    """Which channels carry nothing, and by how much they missed.

    Two rules, and a channel need fail only one: far enough under the
    loudest is an input nobody plugged anything into, and under the
    absolute floor there is only converter noise. The absolute rule
    applies only where one channel is above it. Returns ([silent],
    [reason]), the reason naming which rule caught it and by how much.
    """
    if not level:
        return [], []
    highest = max(level)
    floor = QUIET_BELOW_DBFS if highest > QUIET_BELOW_DBFS else float("-inf")
    silent, why = [], []
    for x in level:
        gap = (highest - x) if x > float("-inf") else float("inf")
        if not (x > float("-inf")):
            silent.append(True), why.append(("quiet", float("-inf")))
        elif gap > SILENT_BELOW_DB:
            silent.append(True), why.append(("under", gap))
        elif x < floor:
            silent.append(True), why.append(("quiet", x))
        else:
            silent.append(False), why.append(None)
    return silent, why



def channel_recipe_mark():
    """The mark for the channel measurement, so a change throws it away."""
    return recipe_mark("channels", channel_facts, channel_levels,
                       channel_hush, channel_rate)


def channel_facts_name():
    """The one name the channel measurement is stored under.

    Built in one place because three ask for it: the one that stores,
    and the two that ask whether it is there. Spelled out twice, the
    recipe mark went into the store and not into the question -- and
    the answer was then "not measured" for ever, which put the work
    back in the queue every time the rows were drawn.
    """
    return "channelfacts-" + channel_recipe_mark()


def channel_facts(file_path, rate=None, stream=0):
    """Measure the channels of one file: how loud, how empty, how alike.

    Every neighbouring pair is measured, not every second one: on a
    mixer, channels 2 and 3 can be the stereo pair as well as 1 and 2.
    So entry k of *pair_same* and *pair_zero* is about channels k and
    k+1, and those lists are one shorter than the channel count.
    *pair_places* says how many places could be measured at all.
    """
    if rate is None:
        rate = channel_rate(file_path, channel_count(file_path))
    try:
        rows = channel_levels(file_path, rate, stream)
    except Exception:
        rows = []
    n = len(rows)
    width = min((len(x) for x in rows), default=0)
    if not n or width < rate // 4:
        return {"channels": n, "level": [], "silent": [], "pair_same": [],
                "pair_zero": [], "pair_apart": [], "pair_places": [],
                "pair_agreed": [], "readable": False}
    rows = [x[:width] for x in rows]
    level = []
    for x in rows:
        top = float(np.percentile(np.abs(x), 99))
        level.append(20.0 * math.log10(top) if top > 0 else float("-inf"))
    highest = max(level)
    silent, why = channel_hush(level)
    pair_same, pair_zero, pair_apart = [], [], []
    pair_places, pair_agreed = [], []
    for a in range(0, n - 1):
        b = a + 1
        if silent[a] or silent[b]:
            pair_same.append(None)
            pair_zero.append(None)
            pair_apart.append(None)
            pair_places.append(None)
            pair_agreed.append(None)
            continue
        with np.errstate(invalid="ignore"):
            r = np.corrcoef(rows[a], rows[b])[0, 1]
        pair_same.append(float(r) if np.isfinite(r) else None)
        share, places, apart, agreed = channel_at_zero(
            rows[a], rows[b], rate)
        enough = places >= PAIR_ENOUGH_PLACES
        pair_zero.append(share if enough else None)
        pair_apart.append(apart if enough else None)
        pair_places.append(places)
        pair_agreed.append(agreed)
    return {"channels": n, "level": level, "silent": silent,
            "pair_same": pair_same, "pair_zero": pair_zero,
            "pair_apart": pair_apart, "pair_places": pair_places,
            "pair_agreed": pair_agreed, "readable": True}


def hush_reason(which, why):
    """Say why a channel counts as carrying nothing, with the number.

    Two rules catch a channel and they are different recording faults:
    nothing plugged in, against a level so low that only the converter's
    own noise is left. One wording for both would be wrong for the
    first -- a channel far under the loudest can still be well above it.
    """
    reason = why[which - 1] if 0 < which <= len(why) else None
    if reason and reason[0] == "under" and reason[1] < float("inf"):
        return T('Channel %d is %s dB under the loudest -- nothing '
                 'plugged in') % (which, decimal_text("%.0f" % reason[1]))
    if reason and reason[1] > float("-inf"):
        return T('Channel %d at %s dBFS -- only converter noise '
                 'left') % (which, decimal_text("%.0f" % reason[1]))
    return T('Channel %d is silent -- unused input') % which



def kind_makes_stereo(kind, channels):
    """Is a two-channel file stereo because of what it is?

    An intro or an outro is a finished stereo mix, not two microphones,
    and the measurement is at its weakest on exactly that material:
    music has no speech pauses and an effect laid on afterwards can
    produce any correlation. Two channels only -- with three or more
    the measurement decides again.
    """
    return (kind in (TYPE_INTRO, TYPE_OUTRO)
            and int(channels or 0) == 2)


def apart_places(agreed, places):
    """How many places the spacing rests on, as a piece of the line.

    Empty where there is nothing to say. Without it a distance out of
    one place of a hundred reads exactly like one out of all of them.
    """
    if not agreed or not places:
        return ""
    return T(', agreed at %s of %s places') % (group_text(agreed),
                                              group_text(places))


def channel_joins(facts, kind=None):
    """Judge every pair of neighbours: could these two be one stereo track?

    Returns [(k, stereo, certain, reason)], k the left channel. Every
    neighbour is asked, not every second one -- fixed pairs would get a
    confident wrong answer. What decides is *when* the two channels hear
    the same thing, not how alike. Where nothing can be measured no pair
    is proposed: two speakers in one track is the error nobody sees.
    """
    # Not seen by this: two recordings laid on a common time axis
    # before being put into one file. Aligning them removes the very
    # delay measured here, and the pair then looks like one.
    n = int(facts.get("channels") or 0)
    if not facts.get("readable") or n <= 1:
        return []
    if kind_makes_stereo(kind, n):
        return [(0, True, True,
                 T('an intro or outro with two channels is a stereo '
                   'mix -- not measured'))]
    silent = list(facts.get("silent") or [False] * n)
    _, why = channel_hush(list(facts.get("level") or []))
    same = list(facts.get("pair_same") or [])
    zero = list(facts.get("pair_zero") or [])
    apart = list(facts.get("pair_apart") or [])
    counted = list(facts.get("pair_places") or [])
    from_agreed = list(facts.get("pair_agreed") or [])
    out = []
    for k in range(n - 1):
        r = same[k] if k < len(same) else None
        at_zero = zero[k] if k < len(zero) else None
        late = apart[k] if k < len(apart) else None
        places = counted[k] if k < len(counted) else None
        # How many places the spacing was read from, against how many
        # were usable at all. A distance is only worth naming when it
        # turns up over and over -- see pair_spacing.
        stood_on = apart_places(
            from_agreed[k] if k < len(from_agreed) else None, places)
        # What belongs on a row in the file list is the answer, not the
        # arithmetic behind it. What was measured is in channel_at_zero.
        if silent[k] or silent[k + 1]:
            which = (k + 2) if silent[k + 1] else (k + 1)
            out.append((k, False, True, hush_reason(which, why)))
        elif r is not None and r >= SAME_SIGNAL:
            out.append((k, True, True,
                        T('both channels identical -- mono laid on both '
                          'sides')))
        elif at_zero is not None and at_zero < PAIR_AT_ZERO:
            # 343 m/s: the delay is the spacing, and giving it in
            # metres is what lets anyone check the answer against the
            # room the recording was made in.
            out.append((k, False, True,
                        T('probably two microphones -- about %s m '
                          'apart%s')
                        % (decimal_text("%.1f" % ((late or 0.0) * 0.343)),
                           stood_on)))
        elif at_zero is not None and at_zero >= PAIR_AT_ZERO:
            # The share is high enough. Two more questions before this
            # is called a pair, because the share alone answers "yes"
            # for every microphone in the same room.
            metres = (late or 0.0) * 0.343
            beside = [zero[j] for j in (k - 1, k + 1)
                      if 0 <= j < len(zero) and zero[j] is not None]
            if metres > PAIR_APART_METRES:
                # Measured apart, so not one place, however well the two
                # agree. Same wording as the plain two-microphone case:
                # it is the same finding, reached the long way round.
                out.append((k, False, True,
                            T('probably two microphones -- about %s m '
                              'apart%s')
                            % (decimal_text("%.1f" % metres), stood_on)))
            elif beside and at_zero - max(beside) < PAIR_STANDS_OUT:
                out.append((k, False, False,
                            T('not recognisable -- these two agree no '
                              'better than each does with the channel '
                              'beside it')))
            else:
                out.append((k, True, True,
                            T('probably one stereo track -- both '
                              'microphones in the same place')))
        else:
            # Nothing was measured here, so nothing is said about what
            # the two channels have in common: the number is what tells
            # a quiet recording from two channels that really share
            # nothing.
            out.append((k, False, False,
                        T('not recognisable -- only %s of %s places '
                          'where both channels carry sound, %s needed')
                        % (group_text(places or 0), group_text(PAIR_PLACES),
                           group_text(PAIR_ENOUGH_PLACES))))
    return out


def joined_channels(facts, choice=None, kind=None):
    """Which neighbours are actually joined, after the ticks.

    A channel belongs to at most one pair, so the answer has to be a set
    that does not overlap. Walking from the left and taking the first
    join that fits is what the interface shows too. Returns
    {left channel: True} for every pair that is joined.
    """
    judged = {k: stereo
              for k, stereo, _sure, _why in channel_joins(facts, kind)}
    picked = dict(choice or {})
    n = int(facts.get("channels") or 0)
    silent = list(facts.get("silent") or [])

    def possible(k):
        """An unused input cannot be one side of a stereo track.

        The interface offers no tick where one of the two is silent, but
        a tick made earlier outlives the measurement it was made under:
        take a block away and what carried something may not any more.
        """
        return not ((k < len(silent) and silent[k])
                    or (k + 1 < len(silent) and silent[k + 1]))

    # First what the measurement proposes, on its own: from the left,
    # each pair it found, skipping what is already spoken for.
    out, taken = {}, set()
    for k in range(max(0, n - 1)):
        if k in taken or (k + 1) in taken or not possible(k):
            continue
        if judged.get(k, False):
            out[k] = True
            taken.update((k, k + 1))
    # Then the hand, as a correction of that proposal rather than an
    # exception inside it. A tick taken away means one pair fewer and
    # nothing else; a tick set means one pair more, and its two
    # neighbours lose theirs.
    for k in sorted(picked):
        if not (0 <= k < n - 1):
            continue
        if not picked[k]:
            out.pop(k, None)
            continue
        if not possible(k):
            continue
        out.pop(k - 1, None)
        out.pop(k + 1, None)
        out[k] = True
    return out


def channel_name(name, channels):
    """What a track cut out of a file is called: "Mixer Channel 1+2".

    "Channel" stays English in every language: it is the word on the
    recorder and in every manual, and translating it would mean the
    interface and the hardware no longer match. A plus joins a pair
    rather than an ampersand, which splits a command in every shell.
    """
    return "%s Channel %s" % (name, "+".join(str(c + 1) for c in channels))


def _level_of(facts, k):
    """Return the level of one channel, a low number where there is none."""
    row = facts.get("level") or []
    if k >= len(row) or row[k] == float("-inf"):
        return -120.0
    return float(row[k])


def wav_safe(target):
    """["-rf64", "auto"] where the target is a WAV, [] where it is not.

    A plain WAV keeps its sizes in 32 bit and stops at 4 GiB. Past that
    ffmpeg writes a header naming less than what is there, every reader
    believes the header, and the tail is gone with nothing saying so.
    RF64 is the same file with 64 bit sizes, and "auto" only switches
    when needed. Only for WAV: ffmpeg refuses the option elsewhere.
    """
    return (["-rf64", "auto"]
            if os.path.splitext(target)[1].lower() == ".wav" else [])


def audio_stream_facts(file_path, stream=0):
    """What ffprobe says about one audio stream, counted among its own.

    *stream* is the number the rest of the program uses -- the nth audio
    stream, 0:a:N to ffmpeg -- not the position in the whole stream
    list. Nothing there means an empty answer, read the same way by all.
    """
    try:
        only_audio = [x for x in ffprobe_json(file_path).get("streams", [])
                      if x.get("codec_type") == "audio"]
    except Exception:
        return {}
    if not only_audio:
        return {}
    return only_audio[stream] if 0 <= stream < len(only_audio) else {}


def pcm_kind(file_path, stream=0):
    """Return the wav sample format to write a copy of this audio in.

    As deep as the original, no deeper: writing a 16 bit recorder file
    as 24 bit costs half again in size and adds nothing. Asked about the
    stream it was given -- a camera file with a 16 bit mix first and 24
    bit takes behind it was being copied out at the depth of the mix.
    """
    a = audio_stream_facts(file_path, stream)
    if str(a.get("sample_fmt") or "").startswith(("flt", "dbl")):
        return "pcm_f32le"
    # bits_per_raw_sample is missing for 16 bit files, so
    # bits_per_sample answers as well. Both absent means unknown, and
    # 24 bit is the safe guess: too deep costs space, too shallow
    # throws away what was recorded.
    deep = 0
    for key in ("bits_per_raw_sample", "bits_per_sample"):
        try:
            deep = int(a.get(key) or 0)
        except (TypeError, ValueError):
            deep = 0
        if deep:
            break
    return "pcm_s16le" if 0 < deep <= 16 else "pcm_s24le"


def split_target(file_path, channels, folder):
    """Where the track made of these channels is written.

    The name says which channels are in it, in the words the file list
    uses. Two things must be unique: the channels, or channel 12 lands
    on the file of 1 and 2; and the source, since every piece goes into
    one folder and two cards with the same file name would overwrite.
    The trailing digit carries a mark, or it would read as a counter.
    """
    stem = os.path.splitext(os.path.basename(file_path))[0]
    tag = "+".join(str(c + 1) for c in channels)
    mark = hashlib.sha1(os.path.abspath(file_path).encode(
        "utf-8", "replace")).hexdigest()[:8]
    return os.path.join(folder, "%s_%s_Channel%s.wav"
                        % (safe_filename(stem)[:60], mark, tag))


def split_channels(file_path, channels, target, stream=0, rate=None):
    """Write one track of a multichannel file into a file of its own.

    *channels* is which channels the track is made of. Everything else
    stays as recorded; *rate* forces a sample rate, needed for camera
    audio at 44.1 kHz while the rest of the run is at 48. The recording
    time goes with the piece: everything after this asks the piece, and
    without it a real pause between blocks would be swallowed.
    """
    channels = tuple(channels)
    if len(channels) == 1:
        pan = "pan=mono|c0=c%d" % channels[0]
    else:
        pan = "pan=stereo|c0=c%d|c1=c%d" % (channels[0], channels[1])
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    stamp = []
    start = bext_time_reference(file_path)
    if start is not None:
        # Counted in samples, so a changed rate changes the number.
        try:
            was = int(ffprobe_json(file_path)["streams"][stream_index_of(
                file_path, stream)]["sample_rate"])
        except Exception:
            was = SR
        now = int(rate or was)
        stamp = ["-write_bext", "1", "-metadata", "time_reference=%d"
                 % int(round(start * now / float(was or now)))]
    shell_quote(["ffmpeg", "-v", "error", "-i", file_path,
                 "-filter_complex", "[0:a:%d]%s[o]" % (stream, pan),
                 "-map", "[o]"]
                + (["-ar", str(rate)] if rate else [])
                + stamp
                + ["-c:a", pcm_kind(file_path, stream)]
                    + wav_safe(target) + ["-y", target])
    return target


def stream_index_of(file_path, audio_number=0):
    """Return the index in the stream list of this audio stream."""
    every = ffprobe_json(file_path).get("streams", []) or []
    seen = -1
    for i, x in enumerate(every):
        if x.get("codec_type") == "audio":
            seen += 1
            if seen == audio_number:
                return i
    return 0


def tracks_to_split(file_path, facts, choice=None, name=None):
    """Return the tracks a file has to be cut into, as [(channels, label)].

    Empty where nothing has to happen: a single channel, or one pair
    that stays together. Silent channels are not in the answer -- an
    unused recorder input must not become a speaker. *name* is what the
    tracks are called; without it the file name does the work.
    """
    rows = channel_tracks(facts, name or os.path.splitext(
        os.path.basename(file_path))[0], choice)
    if len(rows) <= 1 and not any(silent for _c, _l, silent in rows):
        return []
    return [(chs, label) for chs, label, silent in rows
            if not silent and chs]


def expand_chains_to_tracks(chains, split_of):
    """Turn recordings into tracks where one file holds several.

    A recorder writing four channels gives four tracks, and a recording
    of three blocks gives three blocks per track, so the blocks are cut
    first and the pieces regrouped. Grouped on the original files, never
    on the pieces: those are named after their channel, and the search
    for continuations would take channel two for the next block.
    """
    out = []
    for row, discarded in chains:
        pieces = [list(split_of(x) or []) for x in row]
        how_many = max((len(x) for x in pieces), default=0)

        def which(row_of_pieces):
            """The channels each piece is made of, in order.

            Counting the pieces is not enough: one block cut into
            [1][2][3+4] and the next into [1+2][3][4] both give three,
            and zipping them would put two different signals on one row.
            """
            out = []
            for x in row_of_pieces:
                stem = os.path.splitext(os.path.basename(x))[0]
                mark = SPLIT_MARK.search(stem)
                out.append(mark.group(0) if mark else stem)
            return out

        # A recording whose blocks did not all come apart the same way
        # stays whole: two different signals on one row would be worse
        # than not splitting at all.
        if not how_many or any(len(x) != how_many for x in pieces) \
                or any(which(x) != which(pieces[0]) for x in pieces):
            out.append((row, discarded))
            continue
        for k in range(how_many):
            out.append(([x[k] for x in pieces],
                        discarded if k == 0 else []))
    return out


def audio_shape(file_path):
    """Return (channels, sample rate) -- what has to match to join."""
    try:
        a = next((x for x in ffprobe_json(file_path).get("streams", [])
                  if x.get("codec_type") == "audio"), {})
        return (int(a.get("channels") or 0), int(a.get("sample_rate") or 0))
    except Exception:
        return (0, 0)


def shapes_match(first, second):
    """Report whether two files can be laid end to end at all.

    Channel count and sample rate have to be the same: the channels are
    judged across all blocks, and one that is number three in one block
    and four in the next makes nonsense of that. Bit depth may differ.
    """
    a, b = audio_shape(first), audio_shape(second)
    if not a[0] or not b[0]:
        return True, ""
    if a == b:
        return True, ""
    if a[0] != b[0]:
        return False, (T('%s channels against %s')
                       % (group_text(a[0]), group_text(b[0])))
    return False, (T('%s Hz against %s Hz')
                   % (group_text(a[1]), group_text(b[1])))


def blocks_facts(paths):
    """Judge the channels over a whole recording, not over one block.

    A recording made of blocks is one recording and its channels are the
    same throughout, but the first block alone can be badly wrong -- a
    soundcheck reads as one pair where the show reads as ten tracks. So
    each block is measured on its own and the answers combined, the pair
    judgement taken from the block where that pair is loudest.
    """
    rows = [x for x in (paths or []) if x]
    if not rows:
        return {"channels": 0, "level": [], "silent": [], "pair_same": [],
                "pair_zero": [], "pair_apart": [], "pair_places": [],
                "pair_agreed": [], "readable": False}
    if len(rows) == 1:
        return channel_facts_cached(rows[0])
    return blocks_facts_from([channel_facts_cached(x) for x in rows])


def blocks_facts_from(every):
    """Combine what was measured per block into one answer.

    Apart from blocks_facts so it can be held against made-up numbers.
    """
    every = [f for f in (every or []) if isinstance(f, dict)]
    if not every:
        return {"channels": 0, "level": [], "silent": [], "pair_same": [],
                "pair_zero": [], "pair_apart": [], "pair_places": [],
                "pair_agreed": [], "readable": False}
    usable = [f for f in every if f.get("readable")]
    if not usable:
        return every[0]
    n = max(int(f.get("channels") or 0) for f in usable)
    usable = [f for f in usable if int(f.get("channels") or 0) == n]
    level = []
    for k in range(n):
        seen = [f["level"][k] for f in usable if k < len(f.get("level") or [])]
        level.append(max(seen) if seen else float("-inf"))
    silent, why = channel_hush(level)
    same, zero, apart, counted = [], [], [], []
    agreed = []
    for i, a in enumerate(range(0, n - 1)):
        b = a + 1
        if silent[a] or silent[b]:
            same.append(None), zero.append(None), apart.append(None)
            counted.append(None)
            continue
        # The block where this pair is loudest: judging a pair on the
        # block where it is silent measures the converter's noise.
        best, loudest = None, float("-inf")
        for f in usable:
            measured = f.get("pair_zero") or []
            if i >= len(measured) or measured[i] is None:
                # This block did not measure the pair -- one of the two
                # was silent in it. Taking its answer would mean taking
                # no answer at all.
                continue
            here = min(_level_of(f, a), _level_of(f, b))
            if here > loudest:
                best, loudest = f, here
        def of(name):
            """Entry i of one of the block's lists, or nothing.

            Guarded one by one: hand-made facts are this function's
            documented input, and there the three lists can be of
            different lengths.
            """
            row = (best or {}).get(name) or []
            return row[i] if i < len(row) else None

        same.append(of("pair_same"))
        zero.append(of("pair_zero"))
        apart.append(of("pair_apart"))
        agreed.append(of("pair_agreed"))
        # The place count comes from the block the answer comes from.
        # Where no block could measure the pair there is no such block,
        # and the number to report is the one the best of them reached
        # -- the row says how close it came, not zero.
        if best is not None:
            counted.append(of("pair_places"))
        else:
            reached = [(f.get("pair_places") or [])[i] for f in usable
                       if i < len(f.get("pair_places") or [])]
            reached = [x for x in reached if x is not None]
            counted.append(max(reached) if reached else None)
    return {"channels": n, "level": level, "silent": silent,
            "pair_same": same, "pair_zero": zero, "pair_apart": apart,
            "pair_places": counted, "pair_agreed": agreed,
            "readable": True}


def channel_facts_cached(file_path):
    """Measure a file's channels once, not once per redraw.

    Reading every channel of an hour of audio takes seconds, and the
    file list is rebuilt on every change. Keyed on size and modification
    time, so a changed file is measured again.
    """
    # Kept on disc, unlike most: reading every channel of an hour of
    # audio takes 20 to 50 seconds, and without this every start of
    # the program does it again. "channels" alone is the plain count.
    return probe_remember(channel_facts_name(), file_path,
                          lambda: channel_facts(file_path),
                          keep=True, as_json=True)


def channel_tracks(facts, name="Track", choice=None):
    """Return the tracks one file contributes, after the pair judgement.

    *choice* overrides the proposal per pair, {left channel: joined},
    which is what the tick in the file list writes. Returns
    [(channels, label, silent)]; *channels* is a tuple of indices, two
    for a stereo pair and one otherwise, or empty where the file has
    only one channel and stays as it is.
    """
    n = int(facts.get("channels") or 0)
    if not facts.get("readable") or n <= 1:
        silent = (facts.get("silent") or [False])
        return [((), name, bool(silent and silent[0]))]
    silent = list(facts.get("silent") or [False] * n)
    joined = joined_channels(facts, choice)
    out, k = [], 0
    while k < n:
        if joined.get(k):
            out.append(((k, k + 1), channel_name(name, (k, k + 1)),
                        silent[k] and silent[k + 1]))
            k += 2
            continue
        out.append(((k,), channel_name(name, (k,)), silent[k]))
        k += 1
    # One track left over means the numbering says nothing -- then the
    # file name alone is the better label.
    awake = [t for t in out if not t[2]]
    if len(awake) == 1:
        out = [(t[0], name if t is awake[0] else t[1], t[2]) for t in out]
    return out


def mix_width(tracks):
    """How many channels a mix of these tracks is delivered in.

    Two where there are several: a mix is what is listened to and
    measured, and two channels is the form it is delivered in. One
    recording is the exception -- nothing to mix, so nothing is widened.
    A stereo source raises the count on its own either way.
    """
    if len(tracks) > 1:
        return 2
    return max(1, widest_track([track.get("ready") or track.get("axis")
                                for track in tracks])) if tracks else 1


def mix_tracks(sources, target, gain=0.0, curve=None, channels=1):
    """Sum several equally long tracks into one.

    The gain and the limiter curve are the same for all tracks, so the
    single tracks add up to exactly the mix again. channels=2 asks for
    two, and a stereo source raises that on its own. The widening
    happens before the sum, the only way a stereo source keeps its
    sides, and by "c1=c0" -- a plain conversion loses three decibels.
    """
    have = [kept_channels(p) for p in sources]
    channels = max(channels, max(have) if have else 1)
    if (len(sources) == 1 and abs(gain) < 0.01 and not curve
            and have[0] == channels):
        return sources[0]
    parts, chains, markers = [], [], []
    for i, path in enumerate(sources):
        parts += ["-i", path]
        chains.append("[%d:a]%s[m%d]"
                      % (i, channel_filter(have[i], channels), i))
        markers.append("[m%d]" % i)
    fc = ";".join(chains) + ";" + "".join(markers) +\
        "amix=inputs=%d:normalize=0" % len(markers)
    if abs(gain) >= 0.01:
        fc += ",volume=%.3fdB" % gain
    if curve:
        # The same gain curve as on all other tracks, hence a second input
        # rather than a limiter of its own. The curve is brought to the
        # channel count by hand: left to ffmpeg, one curve channel against
        # two of signal would come with the equal-power law and quietly take
        # another 3 dB off everything.
        fc += "[both]"
        parts += ["-i", curve]
        fc += ";[both]aformat=sample_fmts=fltp:sample_rates=%d[gm];" % SR
        fc += "[%d:a]%s,aformat=sample_fmts=fltp:sample_rates=%d[gc];" % (
            len(sources), channel_filter(kept_channels(curve), channels), SR)
        fc += "[gm][gc]amultiply[out]"
    else:
        fc += "[out]"
    # The clock of the first source goes with the mix. Without it a
    # levelled file came out with no timecode at all, and a recording
    # with no clock cannot be placed against anything afterwards -- so
    # the level was left alone wherever the clock still mattered.
    clock = []
    start = bext_time_reference(sources[0])
    if start is not None:
        clock = ["-write_bext", "1", "-metadata",
                 "time_reference=%d" % int(round(start))]
    run_ffmpeg_with_progress(
        ["ffmpeg", "-v", "error"] + parts + ["-filter_complex", fc,
         "-map", "[out]", "-c:a", "pcm_s24le"] + clock
        + wav_safe(target) + ["-y", target],
        sample_count(sources[0]) / float(SR),
        T('Mixing %s') % (os.path.splitext(os.path.basename(target))[0]
                       .replace("mix_", "").replace("single_", "")
                       .replace("full", "Full-Mix")))
    return target


def rate_filter_chain(b):
    """Build a filter chain that compresses a track by factor b.

    The obvious chain rounds to whole sample rates, which at 48 kHz
    means steps of 20.8 ppm -- coarse correction can live with that, the
    fine correction cannot. So the intermediate rate is a hundred times
    higher. The built-in resampler sometimes fails at such ratios and
    soxr does not; without soxr the coarse path is used.
    """
    if soxr_available():
        return ("asetrate=%d,aresample=resampler=soxr:osr=%d,asetrate=%d"
                % (SR * 100, int(round(SR * 100 / b)), SR))
    if abs(b - 1.0) > 1e-7 and not getattr(rate_filter_chain, "warned", False):
        rate_filter_chain.warned = True
        print(T('  Note: this ffmpeg has no soxr -- clock drift can only '
                'be taken out in\n  steps of 21 ppm.'))
    return "asetrate=%d,aresample=%d,asetrate=%d" % (SR, int(round(SR / b)),
                                                     SR)


def place_track_on_axis(source, target, a, b, t0, t1, drift=True):
    """Place an audio track on the reference axis and clip it to [t0, t1].

    Audio time = a + b * reference time. The drift is removed first,
    then the offset divided by b; the track is cut to the window start
    and padded with silence to its full length. Every track gets the
    same window, or Auphonic cannot remove the crosstalk. The channel
    count is the source's; only more than two is folded.
    """
    n_window = int(round((t1 - t0) * SR))
    keep = kept_channels(source)
    af = []
    if drift and abs(b - 1.0) > 1e-7:
        af.append(rate_filter_chain(b))
        start = a / b + t0
    else:
        start = a + t0
    k = int(round(start * SR))
    if k > 0:
        af.append("atrim=start_sample=%d" % k)
        af.append("asetpts=N/SR/TB")
    elif k < 0:
        af.append("adelay=delays=%dS:all=1" % (-k))
    af.append("apad=whole_len=%d" % n_window)
    af.append("atrim=end_sample=%d" % n_window)
    af.append("asetpts=N/SR/TB")
    shell_quote(["ffmpeg", "-v", "error", "-i", source, "-af", ",".join(af),
        "-ac", str(keep), "-c:a", "pcm_s24le"]
            + wav_safe(target) + ["-y", target])
    return target


def envelope_heard(path):
    """The curve of a file's audio, or None where there is none to read.

    A camera that gives nothing is ordinary material: one whose sound
    broke off after a moment, or a file that lost its track in a copy.
    That is not a fault of the run, so it is answered rather than
    raised -- and the caller places the camera by its clock and says
    so, instead of the run stopping on the first line.
    """
    try:
        return video_envelope(path)
    except Exception:
        return None


def place_camera_by_clock(v, position, clocks, reference):
    """Place a camera that gives no sound, by its clock, and say so.

    The measured offset is the reference clock less this camera's own
    -- measured on 3.9.2026 against two cameras five seconds apart,
    a = -5.000 at a quality of 0.912. Both ends therefore come from
    the one reckoning, and where either clock is missing there is
    nothing to place it with and it is refused rather than laid down.
    """
    own, base = clocks.get(v), clocks.get(reference)
    st = {"points": 0, "unplaceable": True, "by_clock_only": True}
    if own is None or base is None or cannot_be_placed(
            st, own, [t for w, t in clocks.items() if w != v]):
        print(as_bad("  " + no_place_message(os.path.basename(v))))
        return
    print(T('  %s gives no sound to measure -- placed by its clock '
            'alone, and nothing was found to check it against')
          % os.path.basename(v))
    position[v] = (base - own, 1.0, st)


def align_cameras(videos):
    """Put all cameras on the time axis of the longest one.

    The longest is the reference because it covers the widest range and
    offers the most sample points. A camera that matches nothing and
    carries no timecode is left out rather than placed: a camera laid
    down at a guess is worse than a missing one, which the log names.
    Returns (reference, {path: (a, b, count)}), camera time = a + b * t.
    """
    heard = dict((v, envelope_heard(v)) for v, _info in videos)
    # The reference has to be one there is something to measure
    # against. The longest of the others otherwise stops the run on
    # its first line -- and the longest is the likeliest reference.
    speaking = [(v, i) for v, i in videos if heard[v] is not None]
    ref_clip = max(speaking or videos, key=lambda v: v[1]["duration"])
    # The reference sits at zero against itself, and nothing had to be
    # measured to find that out.
    position = {ref_clip[0]: (0.0, 1.0, {"points": 0})}
    env_ref = heard[ref_clip[0]]
    clocks = dict((v, timecode_seconds(i)) for v, i in videos)
    for v, info in videos:
        if v == ref_clip[0]:
            continue
        env = heard[v]
        if env is None or env_ref is None:
            place_camera_by_clock(v, position, clocks, ref_clip[0])
            continue
        # Sample more densely than for audio against video: two cameras often
        # overlap only partly, and what lies outside the overlap drops out as a
        # sample point anyway. Every 30 seconds instead of every two minutes,
        # at least 20 points.
        duration = len(env_ref) * 5.0 / 1000.0
        density = int(max(20, min(120, duration / 30.0)))
        try:
            a, b, st = align_envelopes(env_ref, env, sample_points=density,
                                          distance_s=30.0,
                                          warn=os.path.basename(v))
        except Exception as e:
            print(T('  %s cannot be classified: %s')
                  % (os.path.basename(v), e))
            continue
        # There is no phase way between two cameras, so the envelopes
        # are the whole measurement and the floor is higher than
        # anywhere else. A short jingle otherwise gets a number too, and
        # on the axis it shrinks the common window to nothing.
        if (st.get("quality", 0.0) < CAMERA_MATCH_ENOUGH
                and not fit_places_it(st)):
            st["unplaceable"] = True
        if cannot_be_placed(st, clocks.get(v),
                            [t for w, t in clocks.items() if w != v]):
            print(as_bad("  " + no_place_message(os.path.basename(v))))
            continue
        position[v] = (a, b, st)
    return ref_clip, position


def unpack_kind(file_path):
    """The depth to unpack a video's audio at: the one it is in.

    pcm_kind measures it; this caps the one answer that cannot be taken
    literally. AAC probes as floating point, and unpacking it as float
    costs a third more room for nothing that was ever in the file. 24
    bit holds everything a camera delivers, and where nothing can be
    measured pcm_kind already answers 24 bit.
    """
    deep = pcm_kind(file_path)
    return "pcm_s24le" if deep == "pcm_f32le" else deep


def extract_audio_from_video(file_path, tmpdir):
    """Extract one camera's audio unchanged.

    Nothing is folded to mono: a single file may carry different
    material left and right, and that should not be lost.
    """
    file_path = os.path.abspath(file_path)
    stem = os.path.splitext(os.path.basename(file_path))[0]
    target = os.path.join(tmpdir, "%s.wav" % safe_filename(stem))
    info = video_facts(file_path)
    if not info["audio"]:
        raise RuntimeError(T('%s has no audio track.') % os.path.basename(file_path))
    channels = int((info["audio"][0] or {}).get("channels") or 1)
    print(as_head(T('NO AUDIO FILE -- USING THE CAMERA AUDIO')))
    print(T('  from %s, %s')
          % (os.path.basename(file_path), channel_text(channels)))
    command = ["ffmpeg", "-v", "error", "-i", file_path, "-map", "0:a:0",
              "-ar", str(SR), "-c:a", unpack_kind(file_path),
              "-write_bext", "1"]
    if info.get("tc"):
        # The audio starts where the picture starts. Passing the timecode along
        # saves the alignment from guessing.
        try:
            t0 = parse_timecode(info["tc"], max(1.0, info["fps"]))
            command += ["-metadata",
                       "time_reference=%d" % int(round(t0 * SR))]
            print("  Timecode %s" % info["tc"])
        except Exception:
            pass
    show_progress(T('Camera audio'), 0.0)
    shell_quote(command + wav_safe(target) + ["-y", target])
    show_progress(T('Camera audio'), 1.0)
    print("  %s" % os.path.basename(target))
    return target


def extract_audio_for_plan(plan, tmpdir):
    """Extract the camera audio for a finished plan.

    The names come from the interface, one row per camera. The channels
    are the camera's own: two clip-on microphones have already been cut
    into two rows by then, and a real stereo pair should keep its sides.
    """
    pending = [e for e in plan if e.get("camera_audio")]
    if not pending:
        return list(plan)
    step_begin("camera audio")
    # Where the interface has already extracted everything there is nothing to
    # show -- the prework belongs in the interface, not in the log of the run.
    to_fetch = [e for e in pending
                if not (e.get("audio_done")
                        and os.path.exists(e["audio_done"]))]
    if to_fetch:
        print(as_head(T('EXTRACTING CAMERA AUDIO')))
    done = []
    for i, e in enumerate(plan):
        if not e.get("camera_audio"):
            # An ordinary audio recording stays as it is.
            done.append(dict(e))
            continue
        # Where the audio is pulled from is the camera it was recorded on,
        # not the camera the speaker is assigned to.
        v = os.path.abspath(e.get("from_camera") or e["camera"] or e["audio"])
        name = e.get("speakers") or guess_camera_name(v)
        # The interface extracts the audio while names are still being typed.
        # Whatever is there is used.
        already = e.get("audio_done")
        if already and os.path.exists(already) and sample_count(already) > 0:
            fresh = dict(e)
            fresh.update({"audio": already, "blocks": [already],
                        "speakers": name, "upfront": True})
            fresh.setdefault("camera", v)
            done.append(fresh)
            continue
        target = os.path.join(tmpdir, "cameraaudio_%s.wav" % safe_filename(name))
        show_progress(T('Camera audio %s') % name, i / float(len(plan)))
        try:
            shell_quote(["ffmpeg", "-v", "error", "-i", v, "-map", "0:a:0",
                "-ac", str(max(1, channel_count(v))), "-ar", str(SR),
                "-c:a", unpack_kind(v)]
                + wav_safe(target) + ["-y", target])
        except Exception as ex:
            print(T('\n  %s: no audio to extract (%s)')
                  % (os.path.basename(v), ex))
            continue
        pieces = camera_audio_tracks(target, name, tmpdir)
        for piece, label in pieces:
            fresh = dict(e)
            fresh.update({"audio": piece, "blocks": [piece],
                          "speakers": label if len(pieces) > 1 else name})
            fresh.setdefault("camera", v)
            fresh.setdefault("from_camera", v)
            done.append(fresh)
    if to_fetch:
        show_progress(T('Camera audio'), 1.0)
        for e in done:
            if not e.get("camera_audio") or e.get("upfront"):
                continue
            print(T('  %-24s from %s')
                  % (e["speakers"], os.path.basename(e["camera"])))
    if len(done) < 2:
        print(T('  Fewer than two cameras with sound -- too few for '
                'Multitrack.'))
    return done


def camera_audio_tracks(audio, name, folder):
    """Cut a camera's audio into the tracks it holds.

    A camera is not automatically one track: two clip-on microphones on
    one channel each are two people, judged by the same measurement as a
    recorder file. The audio is extracted with every channel it has --
    folding first and then asking what is on it always answers "one
    voice". Returns [(file, name)], one entry where nothing is cut.
    """
    try:
        facts = channel_facts_cached(audio)
        want = tracks_to_split(audio, facts, name=name)
    except Exception:
        want = []
    if not want:
        return [(audio, name)]
    out = []
    for chs, label in want:
        target = split_target(audio, chs, folder)
        try:
            if not os.path.exists(target) or not os.path.getsize(target):
                split_channels(audio, chs, target, rate=SR)
        except Exception as e:
            print(T('  %s: channel %s cannot be cut out (%s)')
                  % (name, "+".join(str(c + 1) for c in chs), e))
            return [(audio, name)]
        out.append((target, label))
    return out


def plan_from_camera_audio(video_paths, tmpdir, cameras=None, title=""):
    """Use each video file's own audio as a track.

    For the case where there are no separate audio recordings, only
    cameras with a built-in or clip-on microphone: each camera becomes a
    track and the crosstalk from the others is removed. A camera
    carrying two microphones becomes two tracks, as a recorder file does.
    """
    step_begin("camera audio")
    plan = []
    prefixes = [t + "_" for t in {title, safe_filename(title)} if t]
    named = ByFile((cam["video"], cam["name"])
                   for cam in (cameras or []) if cam.get("video"))
    taken = set()
    print(as_head(T('NO SEPARATE AUDIO RECORDINGS -- USING THE CAMERA AUDIO')))
    for i, v in enumerate(video_paths, 1):
        v = os.path.abspath(v)
        # The name has to differ per camera: it becomes the track identifier at
        # Auphonic. The file stem serves; nothing is guessed here.
        name = named.get(v) or os.path.splitext(os.path.basename(v))[0]
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
                break
        reason, cam = name, 2
        while name in taken:
            name = "%s %d" % (reason, cam)
            cam += 1
        taken.add(name)
        target = os.path.join(tmpdir, "cameraaudio_%s.wav" % safe_filename(name))
        show_progress(T('Camera audio %s') % name, (i - 1) / float(
            len(video_paths)))
        try:
            shell_quote(["ffmpeg", "-v", "error", "-i", v, "-map", "0:a:0",
                "-ac", str(max(1, channel_count(v))), "-ar", str(SR),
                "-c:a", unpack_kind(v)]
                + wav_safe(target) + ["-y", target])
        except Exception as e:
            print(T('\n  %s: no audio to extract (%s)')
                  % (os.path.basename(v), e))
            continue
        for piece, label in camera_audio_tracks(target, name, tmpdir):
            plan.append({"audio": piece, "blocks": [piece],
                         "speakers": label, "camera": v,
                         "from_camera": v})
    show_progress(T('Camera audio'), 1.0)
    for e in plan:
        print(T('  %-24s from %s') % (e["speakers"],
                                  os.path.basename(e["camera"])))
    if len(plan) < 2:
        print(T('  Fewer than two cameras with sound -- too few for '
                'Multitrack.'))
    return plan


def clocks_on_the_axis(videos, position, tracks, ref_clip):
    """Every file besides the reference that knows the time of day.

    One entry per file that carries a timecode and whose place on the
    axis was measured: the name to say it by, the clock in seconds, and
    the place (file time = a + b * axis time). A file that was never
    placed is left out -- its clock says when it was recorded but not
    where it sits, and only the two together say what the reference's
    first frame reads.
    """
    found = []
    for v, info in videos:
        if v == ref_clip[0] or v not in position:
            continue
        when = timecode_seconds(info)
        if when is None:
            continue
        a, b, _st = position[v]
        found.append({"name": os.path.basename(v), "tc": when,
                      "a": a, "b": b})
    for track in (tracks or []):
        blocks = track.get("blocks") or []
        # The blocks were sorted by time and joined on one axis, so the
        # first one's clock is the clock of the joined recording.
        # A recorder writes no frames, so the frames of a timecode track
        # belong to the reference picture and are read at its rate.
        when = file_timecode(blocks[0], ref_clip[1]["fps"]) if blocks else None
        if when is None:
            continue
        found.append({"name": os.path.basename(blocks[0]), "tc": when,
                      "a": track["a"], "b": track["b"]})
    return found


def axis_starts_at(clocks):
    """What the reference camera's first frame reads on the clock.

    Every file that carries a timecode answers on its own: its clock
    less its own place on the axis. Nothing, where none answers.
    """
    # File time = a + b * axis time, so the file's own zero sits at
    # -a / b on the axis, and the reference's zero reads that much
    # earlier on the file's clock.
    says = sorted(float(c["tc"]) + float(c["a"]) / float(c["b"])
                  for c in clocks)
    # The median, so one clock never set right cannot move the window:
    # in one production two cameras disagreed by two seconds. It is
    # also the rule measure_time_axis ties the preview's axis by, so
    # what is marked in the player and what the run makes of it agree.
    return says[len(says) // 2] if says else None


def clip_to_time_window(args, t0, t1, ref_clip, clocks=()):
    """Apply the In point and the Out point to the measured window.

    The window lives in reference camera time. An absolute value is
    converted through a timecode; a relative one counts from the window
    start, a negative one back from the window end. *clocks* is what
    else on the axis knows the time of day, in the shape axis_starts_at
    wants -- the reference is the longest camera and need not carry a
    clock of its own.
    """
    start = getattr(args, "in_point", None)
    end = getattr(args, "out_point", None)
    if not start and not end:
        return t0, t1
    fps = max(1.0, ref_clip[1]["fps"]) if ref_clip else 30.0
    tc_ref, tc_from = None, ""
    if ref_clip and ref_clip[1].get("tc"):
        tc_ref = parse_timecode(ref_clip[1]["tc"], fps)
    elif clocks:
        # No clock of its own, but the axis hangs on the clocks around
        # it, and that is a number the alignment has already measured.
        tc_ref = axis_starts_at(clocks)
        tc_from = ", ".join(sorted(c["name"] for c in clocks))

    def convert(value_text, from_the_end):
        value, absolute = parse_time_point(value_text, fps)
        if value is None:
            return None
        if absolute:
            # Two different situations, and one message for both used to
            # name a reference camera that does not exist on the path
            # without a picture.
            if tc_ref is None and not ref_clip:
                raise RuntimeError(
                    T('%r is a Timecode, but there is no picture here and '
                      'so no camera to count it from. Then only a value '
                      'from the window start works, such as +12:30.')
                    % value_text)
            if tc_ref is None:
                raise RuntimeError(
                    T('%r is a Timecode, but the time axis hangs on no '
                      'clock: no file here carries one, the reference '
                      'camera %s included. Then only a value from the '
                      'window start works, such as +12:30.')
                    % (value_text, os.path.basename(ref_clip[0])))
            return value - tc_ref
        if value < 0:
            if not from_the_end:
                raise RuntimeError(
                    T('%r counts from the end -- that only works '
                      'for Out point.') % value_text)
            return t1 + value
        return t0 + value

    try:
        new0 = convert(start, False) if start else t0
        new1 = convert(end, True) if end else t1
    except RuntimeError as e:
        print("\n%s" % e)
        return None, None
    print(T('\n  Time window by hand:'))
    if tc_from:
        # Which clocks the axis was hung on, and what it makes the
        # reference's first frame read. Without this the two lines below
        # are a number nobody can check: the reference camera carries no
        # timecode, so a reader would look for one there and find none.
        print(T('    The reference camera carries no Timecode. The axis '
                'hangs on the clock of %s, and its first frame reads %s.')
              % (tc_from, timecode_string(tc_ref, fps)))
    if tc_ref is not None:
        # The reference camera's rate, the same one the axis runs at:
        # the two lines say back what was typed in, and at 25 a line
        # printed at 30 would name a different frame.
        print(T('    In point   %s   (Timecode %s)')
              % (as_hms(new0), timecode_string(tc_ref + new0, fps)))
        print(T('    Out point  %s   (Timecode %s)')
              % (as_hms(new1), timecode_string(tc_ref + new1, fps)))
    else:
        print(T('    In point   %s\n    Out point  %s')
              % (as_hms(new0), as_hms(new1)))
    if new1 <= new0:
        print(T('    Out point lies before In point -- that does not work.'))
        return None, None
    outside = []
    if new0 < t0 - 0.001:
        outside.append(T('In point is %s before the first frame')
                          % as_hms(t0 - new0))
    if new1 > t1 + 0.001:
        outside.append(T('Out point is %s after the last frame')
                          % as_hms(new1 - t1))
    if outside:
        print(T('    Careful: %s. There is no picture there;') % T(' and ').join(
            outside))
        print(T('    the measured window is therefore kept.'))
        new0, new1 = max(new0, t0), min(new1, t1)
    if new1 - new0 < 5:
        print(T('    The window would be only %s long -- that cannot be '
                'intended.') % as_hms(max(0, new1 - new0)))
        return None, None
    kept, measured = as_hms(new1 - new0), as_hms(t1 - t0)
    # The bracket is there to say "yours instead of the measured one".
    # Where a point was pulled back the two are the same length, and
    # "1:26:31 (instead of 1:26:31)" says nothing twice.
    print(T('    Length  %s  (instead of %s)') % (kept, measured)
          if kept != measured else T('    Length  %s') % kept)
    return new0, new1


def merge_plan_entries(plan):
    """Merge plan rows that share a speaker name into one track.

    Stopping the recording in between leaves several files for the same
    person; their timecodes place them anyway, and as one track it stays
    one person at Auphonic. A row marked "apart" stays put and is no
    target either: two blocks of one recorder guess the same name, so
    without that mark this undid what --apart had separated.
    """
    combined = []
    after_name = {}
    for e in plan:
        name = (e.get("speakers") or "").strip()
        blocks = list(e.get("blocks") or [e["audio"]])
        if name and name in after_name and not e.get("apart"):
            old = after_name[name]
            old["blocks"] += blocks
            if not old.get("camera") and e.get("camera"):
                old["camera"] = e["camera"]
            elif (e.get("camera") and old.get("camera")
                  and os.path.abspath(e["camera"])
                  != os.path.abspath(old["camera"])):
                print(T('  %s appears twice with different cameras -- %s '
                        'is used')
                      % (name, os.path.basename(old["camera"])))
            continue
        fresh = dict(e)
        fresh["blocks"] = blocks
        fresh["speakers"] = name
        combined.append(fresh)
        if name and not fresh.get("apart"):
            after_name[name] = fresh
    for e in combined:
        e["blocks"] = sort_by_time(e["blocks"])
        e["audio"] = e["blocks"][0]
    more = [(e["speakers"], len(e["blocks"])) for e in combined
            if len(e["blocks"]) > 1]
    if len(combined) < len(plan):
        print(T('  In summary: %s')
              % ", ".join(T('%s from %s recordings') % (n, group_text(k))
                           for n, k in more))
    return combined


def sort_by_time(paths):
    """Sort blocks into recording order: bext timecode, else file name."""
    def api_key(p):
        try:
            tr = bext_time_reference(p)
        except Exception:
            tr = None
        return (0, tr, "") if tr is not None else (1, 0, os.path.basename(p))
    return sorted(paths, key=api_key)


def one_track_left(plan):
    """What to do when the camera audio holds fewer than two tracks.

    Nothing: a single recording is a special case of several, not a
    different kind of job, and it goes the same way. What falls away is
    only the multitrack production, decided where the upload happens.
    Returns 1 for the one case that cannot go on -- no camera had a
    microphone and there is no sound at all -- and None otherwise.
    """
    if not [e["audio"] for e in plan if e.get("audio")]:
        print(as_bad(T('No sound in the cameras -- nothing to work with.')))
        return 1
    return None


def show_multitrack_plan(args, audio_paths, video_paths):
    """Show the detected plan without doing anything yet."""
    step_begin("plan")
    plan, cameras, title = [], [], ""
    if args.assign and os.path.exists(args.assign):
        try:
            with open(args.assign, encoding="utf-8") as f:
                d = json.load(f)
        except ValueError as e:
            print(T('Assignment file not readable: %s') % e)
            return 1
        if isinstance(d, dict):
            complaint = format_complaint(d)
            if complaint:
                print(as_bad(T('Abort: %s') % complaint))
                return 1
            plan = d.get("tracks_of") or []
            cameras = d.get("cameras") or []
            # What the window already had taken apart by voice. Carried
            # over rather than computed again: three minutes of the
            # graphics unit for a result that is already there.
            args._speakers_of = d.get("speakers_of") or {}
            title = d.get("production") or ""
            args.production = title
        else:
            plan = d
    print(as_head(T('RECOGNISED PLAN')))
    if title:
        print(T('  Production at auphonic.com:   %s') % title)
    if not plan and audio_paths:
        # A block taken out by hand is carried as such into the plan.
        # Grouping alone was not enough: the rows are merged by speaker
        # name further down, and two blocks of one recorder guess the
        # same name, so what was separated here was joined again there.
        kept_apart = {path_key(x)
                      for x in (getattr(args, "apart", ()) or ())}
        for row, _ in group_recording_parts(audio_paths,
                                            args.no_follow_ups,
                                            getattr(args, "apart", ()),
                                            getattr(args, "together", ())):
            plan.append({"audio": row[0], "blocks": row,
                         "speakers": guess_speaker_name(row[0]), "camera": "",
                         "apart": any(path_key(b) in kept_apart
                                      for b in row)})
    if any(e.get("camera_audio") for e in plan):
        # The interface sent cameras rather than audio recordings: names and
        # assignment are settled, only the audio is extracted now.
        args._camera_audio = tempfile.mkdtemp(prefix="vpm_camaudio_")
        atexit.register(shutil.rmtree, args._camera_audio, True)
        plan = extract_audio_for_plan(plan, args._camera_audio)
        if len(plan) < 2:
            stop = one_track_left(plan)
            if stop is not None:
                return stop
    elif not plan:
        # Only video files on the command line: guess the names ourselves.
        args._camera_audio = tempfile.mkdtemp(prefix="vpm_camaudio_")
        atexit.register(shutil.rmtree, args._camera_audio, True)
        plan = plan_from_camera_audio(video_paths, args._camera_audio, cameras, title)
        if len(plan) < 2:
            stop = one_track_left(plan)
            if stop is not None:
                return stop
        if not cameras:
            # One entry per camera, not per track: a camera whose two
            # channels carry two microphones is still one camera and
            # still writes one file. Both names go into that file name.
            who = ByFile()
            for e in plan:
                who.setdefault(e["camera"], []).append(
                    e["speakers"])
            cameras = [{"video": v, "name": "%s_%s"
                        % (safe_filename(title or 'Production'),
                           "+".join(names))}
                       for v, names in who.items()]
    if not cameras and video_paths:
        # No assignment file and no names from the plan: one entry per
        # video file, named after the file plus the suffix. Without this
        # the run wrote camera files under the source's own name and no
        # handover at all, which is what the whole run is for.
        cameras = [{"video": os.path.abspath(path),
                    "name": os.path.splitext(os.path.basename(path))[0]
                            + (args.suffix or "_audio")}
                   for path in video_paths]
    plan = merge_plan_entries(plan)
    for e in plan:
        blocks = e.get("blocks") or [e["audio"]]
        total = sum(sample_count(b) for b in blocks) / float(SR)
        target = os.path.basename(e["camera"]) if e.get("camera")\
            else label_of(MIX_ONLY)
        print("  %-20s %-34s %s%s"
              % (e.get("speakers") or T('unnamed'),
                 os.path.basename(blocks[0])
                 + ("  (+%d)" % (len(blocks) - 1) if len(blocks) > 1 else ""),
                 as_hms(total), "  ->  " + target))
    combined = {}
    for e in plan:
        combined.setdefault(e.get("camera") or "", []).append(
            e.get("speakers") or "?")
    multiple = {cam: v for cam, v in combined.items() if len(v) > 1 and cam}
    for cam, v in multiple.items():
        print(T('  %s gets %s tracks mixed together: %s')
              % (os.path.basename(cam), group_text(len(v)), ", ".join(v)))
    if cameras:
        print(T('\n  This produces:'))
        every = [e.get("speakers") or "?" for e in plan]
        # The same rule the writer follows: a recording gets a line of
        # its own only where no camera has a track at all, there is more
        # than one recording, and --no-single-tracks was not given.
        singles = ([] if any(k for k in combined) or len(every) < 2
                   or getattr(args, "no_single_tracks", False) else every)
        for cam in cameras:
            own = combined.get(cam["video"]) or []
            print("    %s  ->  %s" % (os.path.basename(cam["video"]),
                                      cam["name"] + ".mov"))
            for idx, what in enumerate(
                    track_order_for_camera(own, every, singles), 1):
                print(T('        Track %d: %s') % (idx, what))
    return build_common_timebase(args, plan, cameras, video_paths, title)


def multitrack_or_single(args, ap, audio_paths, video_paths):
    """Take the multitrack path, or the ordinary one where one track is left.

    How many tracks there are is not how many files there are: a camera
    carrying two clip-on microphones is two. That is measured while the
    plan is built, so the decision falls after the plan and not on a
    file count before anybody has looked.
    """
    return show_multitrack_plan(args, audio_paths, video_paths)


def join_the_plan(plan, tmpdir):
    """Join the blocks of every track. No camera is needed for that."""
    made = []
    for e in plan:
        blocks = e.get("blocks") or [e["audio"]]
        name = e.get("speakers") or os.path.basename(blocks[0])
        if len(blocks) > 1:
            source, join_info = join_with_report(
                blocks, os.path.join(tmpdir,
                                     "raw_%s.wav" % safe_filename(name)))
            hint = T('%s blocks') % group_text(join_info["blocks"])
        else:
            source, hint = blocks[0], ""
        made.append({"name": name, "source": source, "hint": hint,
                     "blocks": list(blocks), "camera": e.get("camera") or ""})
    return made


def join_only(args, tracks, tmpdir, title=""):
    """Join the blocks and stop: there is no picture to lay them on.

    Joining the blocks of a recording needs no camera, and one file out
    of several is a whole result.
    """
    first = tracks[0]["blocks"][0]
    folder = os.path.abspath(args.out) if args.out else os.path.dirname(
        os.path.abspath(first))
    # Measured, said, and adjusted where a target was given -- the same
    # as on any run with a picture. One gain per recording, because
    # without a picture they are not laid against each other and there
    # is no balance between them to keep.
    for track in tracks:
        try:
            gain, curve = normalise_loudness(
                [{"name": track["name"], "axis": track["source"],
                  "ready": track["source"]}], args.lufs, tmpdir, None,
                channels=channel_count(track["source"]))
        except Exception as e:
            gain, curve = 0.0, None
            print(T('  Loudness not measurable: %s') % str(e)[:60])
        if gain or curve:
            track["source"] = mix_tracks(
                [track["source"]],
                os.path.join(tmpdir, "level_%s.wav"
                             % safe_filename(track["name"])),
                gain, curve, channels=channel_count(track["source"]))
    if args.auphonic_key:
        key = api_key_from_anywhere(args)
        preset, presetname = choose_preset(
            key, args.auphonic_preset, len(tracks) > 1, lufs=args.lufs,
            anyway=getattr(args, "anyway", False))
        for track in tracks:
            track["axis"] = track["source"]
            track["done"] = run_single_production(
                track["source"], preset, presetname, key, folder,
                args.auphonic_wait, args.dry_run, title or track["name"])
        if args.dry_run:
            return 0
        # What came back is held against what went up, the same as on a
        # run with a picture. The service can prepend material and
        # change the length, and nothing else here would notice.
        longest = max(sample_count(t["source"]) for t in tracks) / float(SR)
        return 0 if verify_returned_tracks(tracks, longest, tmpdir) else 1
    if len(tracks) == 1 and len(tracks[0]["blocks"]) < 2:
        print(T('Only one audio file and no picture -- nothing to do.'))
        return 0
    os.makedirs(folder, exist_ok=True)
    written = []
    for track in tracks:
        stem = os.path.splitext(os.path.basename(track["blocks"][0]))[0]
        counted = TRAILING_NUMBER.match(stem)
        if counted:
            stem = counted.group(1).rstrip("_-. ")
        target = os.path.join(folder, stem + "_joined.wav")
        if args.dry_run:
            print(T('Would write: %s') % target)
            continue
        shell_quote(["ffmpeg", "-v", "error", "-i", track["source"],
                     "-c:a", "copy", "-y", target])
        written.append(target)
    if written:
        print(as_head(T('RESULT')))
        for target in written:
            print("  %s  (%s)"
                  % (target, as_hms(sample_count(target) / float(SR))))
    return 0


def measure_tracks_against_each_other(tracks):
    """Put every track on the time axis of the longest one.

    The longest recording is the reference for the same reason the
    longest camera is: it overlaps most with the others. Returns the
    tracks that found a place, each carrying a and b.
    """
    reference = max(tracks, key=lambda t: sample_count(t["source"]))
    length = sample_count(reference["source"]) / float(SR)
    print(T('  Reference: %s (%s, longest running time)')
          % (reference["name"], as_hms(length)))
    placed = []
    for track in tracks:
        if track is reference:
            track["a"], track["b"] = 0.0, 1.0
            placed.append(track)
            continue
        try:
            # The same measurement as against a camera, which reads the
            # audio of whatever it is handed and never the picture. A
            # second way of aligning would be a second answer to one
            # question.
            a, b, st = align_audio_to_video(
                track["source"], reference["source"], 0,
                sample_points=int(max(20, min(120, length / 30.0))),
                distance_s=30.0)
        except Exception as e:
            print(T('  %-20s cannot be aligned: %s') % (track["name"], e))
            continue
        if st.get("unplaceable"):
            print(as_bad("  " + no_place_message(track["name"])))
            continue
        track["a"], track["b"] = a, b
        placed.append(track)
        # The same note as on the path with a picture: which way placed
        # it. Without it a track put there by phase shows +0.00 ppm and
        # nothing else, and that reads as a drift measured at zero.
        track["hint"] = which_way_placed(st, track.get("hint") or "")
        print(T('  %-20s offset %s, clock drift %s ppm (+/- %s), '
                'residual spread %s ms, %s of %s points%s')
              % (track["name"], as_hms(a),
                 decimal_text("%+.2f" % st.get("ppm", 0.0)),
                 decimal_text("%.2f" % st.get("ppm_error", 0.0)),
                 decimal_text("%.1f" % st.get("spread_ms", 0.0)),
                 group_text(st.get("points", 0)),
                 group_text(st.get("candidates", 0)),
                 "  [" + track["hint"] + "]" if track.get("hint") else ""))
    return placed


def align_tracks_only(args, tracks, tmpdir, title=""):
    """Lay the tracks against each other where there is no picture.

    Equally long and with the same start point, which is what a
    multitrack production needs. The window holds everything any track
    heard: a silent edge costs less than a recording cut short.
    """
    step_begin("time base")
    print(as_head(T('\nMEASURING THE TIME AXIS')))
    print(T('  No picture: the tracks are laid against each other.'))
    placed = measure_tracks_against_each_other(tracks)
    if len(placed) < 2:
        print(T('\nOnly one track found a place -- there is nothing left '
                'to lay it against.'))
        return 1
    areas = [((0.0 - t["a"]) / t["b"],
              (sample_count(t["source"]) / float(SR) - t["a"]) / t["b"])
             for t in placed]
    first = min(b0 for b0, _ in areas)
    last = max(b1 for _, b1 in areas)
    # Zero is the start of the window, not the reference: a recording
    # that began earlier would otherwise stand at a negative time, and
    # that is nobody's time.
    for track, (b0, b1) in zip(placed, areas):
        track["a"] = track["a"] + track["b"] * first
        track["silence_head"], track["silence_tail"] = b0 - first, last - b1
    print(T('  Window:              %s -- everything any track heard')
          % as_hms(last - first))
    for track in placed:
        if max(track["silence_head"], track["silence_tail"]) <= 0.25:
            continue
        print(T('    %s: silence for %s at the front and %s at the back')
              % (track["name"], as_hms(track["silence_head"]),
                 as_hms(track["silence_tail"])))
    t0, t1 = clip_to_time_window(args, 0.0, last - first, None)
    if t0 is None:
        return 1
    folder = os.path.abspath(args.out) if args.out else os.path.dirname(
        os.path.abspath(placed[0]["blocks"][0]))
    if lufs_does_nothing(args, ()):
        print(T('  --lufs does nothing here: the tracks leave as they '
                'were recorded, and the loudness is set where they are '
                'mixed.'))
    if not args.dry_run:
        os.makedirs(folder, exist_ok=True)
    print(as_head(T('\nWRITING TRACKS TO THE AXIS')))
    for track in placed:
        target = os.path.join(tmpdir if args.dry_run else folder,
                              "%s_aligned.wav" % safe_filename(track["name"]))
        track["drift"] = (not args.no_drift
                          and abs(track["b"] - 1.0) > 1e-7)
        show_progress(track["name"], 0.0)
        place_track_on_axis(track["source"], target, track["a"], track["b"],
                            t0, t1, track["drift"])
        show_progress(track["name"], 1.0)
        print()
        track["axis"] = target
        print("    %s, %s" % (as_hms(sample_count(target) / float(SR)),
                              as_data_size(size_in_mb(target))))
    verify_alignment(placed, t0, t1, drift_allowed=not args.no_drift)
    if args.auphonic_key and not getattr(args, "without_auphonic", False):
        stop = send_aligned_tracks(args, placed, folder, tmpdir, t1 - t0,
                                   title)
        if stop is not None:
            return stop
    if args.dry_run:
        print(T('\n  (measuring only: nothing written)'))
        return 0
    print(as_head(T('RESULT')))
    for track in placed:
        print("  %s  (%s)" % (track["axis"],
                              as_hms(sample_count(track["axis"])
                                     / float(SR))))
    return 0


def send_aligned_tracks(args, tracks, folder, tmpdir, window, title=""):
    """Send the aligned tracks up as one multitrack production.

    Returns a return code where the run is over, and None where it goes
    on. Nothing leaves this machine unless a key was given: that is what
    asking for it looks like on the command line.
    """
    key = api_key_from_anywhere(args)
    try:
        preset, _name = choose_preset(key, args.auphonic_preset, True,
                                      lufs=args.lufs,
                                      anyway=getattr(args, "anyway", False))
    except Exception as e:
        print(T('\nNo preset chosen: %s') % e)
        return 1
    try:
        done = run_multitrack_production(
            key, preset, title or 'Production', tracks, folder,
            args.auphonic_wait, args.dry_run, args.auphonic_resume)
    except Exception as e:
        print(as_bad(T('Processing failed: %s') % e))
        return 1
    if args.dry_run:
        return None
    for track in tracks:
        track["done"] = done.get(track["name"])
    missing = [t["name"] for t in tracks if not t.get("done")]
    if missing:
        print(T('\nEnded without a result: %s') % ", ".join(missing))
        return 1
    return None if verify_returned_tracks(tracks, window, tmpdir) else 1


def build_common_timebase(args, plan, cameras, video_paths, title=""):
    """Put all audio tracks on one common time axis.

    Equally long files with the same start point -- what Auphonic
    requires, and what makes crosstalk removal worth anything.
    """
    step_begin("time base")
    videos = []
    for v in video_paths:
        v = os.path.abspath(v)
        try:
            info = video_facts(v, args.fps, args.tc)
        except Exception as e:
            print(T('  %s: %s, skipped') % (os.path.basename(v), e))
            continue
        if not info["audio"]:
            print(T('  %s has no camera sound -- without it nothing can be '
                    'aligned') % os.path.basename(v))
            continue
        if known_frame_rate(file_frame_rate(info)) is None:
            # Said, not refused: the Timeline takes a rate Resolve has
            # and the file is converted into it. Which rate that is says
            # the note below, where every camera has been read.
            print(T('  %s runs at %s frames/s, a rate Resolve has no '
                    'Timeline for -- it is converted, not left out')
                  % (os.path.basename(v),
                     decimal_text("%.3f" % file_frame_rate(info))))
        videos.append((v, info))
    if videos and not getattr(args, "production", ""):
        # The same name the ordinary path gives a production: the folder
        # the material sits in. Without it two jobs from two shoots
        # wrote the same handover and the second took the first's place.
        args.production = guess_production_name(videos[0][0])
    if not videos:
        if video_paths:
            print(T('\nNo usable video file -- without camera audio there '
                    'is no common time axis.'))
            return 1
        if args.multitrack and len(plan) < 2:
            # Multitrack means one track per voice. Joining what is
            # left would glue two people into one file, so it is not
            # even begun.
            print(T('\nOnly one track is left once the blocks are joined, '
                    'and multitrack needs one per voice. Where two people '
                    'were taken for one recording, --apart keeps a block '
                    'out of it.'))
            return 1
        tmpdir = tempfile.mkdtemp(prefix="vpm_mt_")
        atexit.register(shutil.rmtree, tmpdir, True)
        made = join_the_plan(plan, tmpdir)
        if args.multitrack:
            # Several separate voices and no picture: they are laid
            # against each other instead of against a camera.
            return align_tracks_only(args, made, tmpdir, title)
        # No picture and nobody asked for multitrack: the blocks of one
        # recording become one file, and that is the whole job.
        return join_only(args, made, tmpdir, title)

    # The nominal rates from the container are compared. The measured ones
    # differ by a few ten-thousandths on every camera; no editor goes by that,
    # and a warning about it would be a false alarm every time.
    rates = sorted({round(i.get("nominal") or i["fps"], 3) for _, i in videos})
    sizes = sorted({"%sx%s" % ((i["video"] or {}).get("width"),
                                  (i["video"] or {}).get("height"))
                       for _, i in videos})
    if len(rates) > 1:
        print(as_head(T('\nDIFFERENT FRAME RATES: %s')
                      % ", ".join("%.3f" % r for r in rates)))
        print(T('  The Timeline gets %s: the highest of them, or the '
                'next rate Resolve\n  has above it. Converted upwards '
                'Resolve repeats frames, downwards it\n  throws them '
                'away. Every camera keeps its own rate, and the cut '
                'counts\n  in that one.')
              % decimal_text("%g" % resolve_timeline_rate(
                  timeline_frame_rate(args, videos, None))))
    if len(sizes) > 1:
        print(as_head(T('\nDIFFERENT FRAME SIZES: %s') % ", ".join(sizes)))
        print(T('  Of no consequence for the sound.'))

    print(as_head(T('\nMEASURING THE TIME AXIS')))
    ref_clip, position = align_cameras(videos)
    print(T('  Reference: %s (%s, longest running time)')
          % (os.path.basename(ref_clip[0]), as_hms(ref_clip[1]["duration"])))
    for v, info in videos:
        if v == ref_clip[0]:
            continue
        if v not in position:
            continue
        a, b, st = position[v]
        print(T('  %-20s offset %s, clock drift %s ppm (+/- %s), '
                'residual spread %s ms, %s of %s points')
              % (os.path.basename(v), as_hms(a),
                 decimal_text("%+.2f" % st.get("ppm", 0.0)),
                 decimal_text("%.2f" % st.get("ppm_error", 0.0)),
                 decimal_text("%.1f" % st.get("spread_ms", 0.0)),
                 group_text(st.get("points", 0)),
                 group_text(st.get("candidates", 0))))

    tmpdir = tempfile.mkdtemp(prefix="vpm_mt_")
    # A dozen paths leave this function before the folder is removed at the
    # end; without this a failed run keeps gigabytes of WAV.
    atexit.register(shutil.rmtree, tmpdir, True)
    joined = join_the_plan(plan, tmpdir)
    tracks = []
    # The same rule the cameras follow: where every way of measuring
    # came up empty and no clock places it either, a recording is
    # refused rather than laid down somewhere -- laid down somewhere it
    # looks exactly like one that fits.
    camera_clocks = [timecode_seconds(i) for _v, i in videos]
    for e, made in zip(plan, joined):
        blocks, name = made["blocks"], made["name"]
        source, hint = made["source"], made["hint"]
        try:
            a, b, st = align_audio_to_video(source, ref_clip[0], 0,
                                  sample_points=int(max(20, min(120,
                                      ref_clip[1]["duration"] / 30.0))),
                                  distance_s=30.0)
        except Exception as ex:
            print(T('  %-20s cannot be aligned: %s') % (name, ex))
            continue
        hint = which_way_placed(st, hint)
        if cannot_be_placed(st, file_timecode(blocks[0]) if blocks else None,
                            camera_clocks):
            print(as_bad("  " + no_place_message(name)))
            continue
        tracks.append({"name": name, "source": source, "a": a, "b": b,
                       "st": st, "camera": e.get("camera") or "",
                       # Which recording the sound came out of, kept
                       # apart from the camera the speaker is on: a
                       # camera's audio is extracted into a file of its
                       # own, and only this still names the recording.
                       "from_camera": e.get("from_camera") or "",
                       "blocks": list(blocks), "hint": hint})
        print(T('  %-20s offset %s, clock drift %s ppm (+/- %s), '
                'residual spread %s ms, %s of %s points%s')
              % (name, as_hms(a),
                 decimal_text("%+.2f" % st.get("ppm", 0.0)),
                 decimal_text("%.2f" % st.get("ppm_error", 0.0)),
                 decimal_text("%.1f" % st.get("spread_ms", 0.0)),
                 group_text(st.get("points", 0)),
                 group_text(st.get("candidates", 0)),
                 "  [" + hint + "]" if hint else ""))
    if not tracks:
        print(T('\nNo audio track could be aligned -- there is nothing to '
                'put on the axis.'))
        return 1

    # Window: what every camera saw, limited to what there is audio for.
    # Anything outside would be uploaded silence.
    camera_areas = []
    for v, info in videos:
        if v not in position:
            continue
        a, b, _ = position[v]
        camera_areas.append(((0.0 - a) / b, (info["duration"] - a) / b,
                             os.path.basename(v)))
    audio_areas = []
    for track in tracks:
        n = sample_count(track["source"]) / float(SR)
        audio_areas.append(((0.0 - track["a"]) / track["b"],
                             (n - track["a"]) / track["b"]))
    # The window comes from the cameras alone: what has no picture needs no
    # audio. Where audio is missing it is padded with silence -- a silent
    # stretch beats a shifted one.
    t0, late, t1, early = common_window(camera_areas)
    for track, (b0, b1) in zip(tracks, audio_areas):
        missing_front, missing_back = max(0.0, b0 - t0), max(0.0, t1 - b1)
        # Report only what is really missing inside the chosen window: a camera
        # running before the recorder was switched on is the normal case and
        # irrelevant to the cut.
        track["missing_head"], track["missing_tail"] = missing_front, missing_back
        # And the other way round: what the recording has outside the
        # window and therefore loses. Not the same question, and it is
        # the one somebody asks when the episode comes out shorter than
        # the recording.
        track["dropped_head"], track["dropped_tail"] = (max(0.0, t0 - b0),
                                                        max(0.0, b1 - t1))

    # Not a length in seconds. What decides is how much the alignment
    # could see: it takes a sample point every couple of seconds, and a
    # window holding none of them is the one that says nothing. One rule
    # for both paths, and the number goes into the message to be checked.
    seen = min([st.get("points", 0) for v, (_a, _b, st) in position.items()
                if v != ref_clip[0]] or [0])
    if t1 - t0 <= 0 or (seen == 0 and t1 - t0 < AXIS_MIN_WINDOW_S):
        print(T('\nSound and picture have only %s in common, and the '
                'alignment found %s sample points in it. That is too '
                'little to place anything on.')
              % (as_hms(max(0, t1 - t0)), group_text(seen)))
        return 1
    print(T('  Common window:       %s to %s (%s)')
          % (as_hms(t0), as_hms(t1), as_hms(t1 - t0)))
    # Name the two cameras that decide it. Without this the window is a
    # number nobody can check, and the question "why is my episode
    # shorter than the material" has no answer in the log.
    print(T('    it begins with %s and ends with %s -- the stretch every '
            'camera saw')
          % (late, early))
    # What falls away, said out loud: the numbers were computed above
    # and printed nowhere, so a run that dropped eight seconds looked
    # like one that dropped nothing.
    for track in tracks:
        front, back = track["dropped_head"], track["dropped_tail"]
        if front <= 0.25 and back <= 0.25:
            continue
        print(T('    %s: %s at the front and %s at the back have no '
                'picture and are left out')
              % (track["name"], as_hms(front), as_hms(back)))
    # Remember the measured window: already processed tracks come from a run
    # without In point and Out point and are therefore exactly that long.
    full0, full1 = t0, t1
    t0, t1 = clip_to_time_window(args, t0, t1, ref_clip,
                                 clocks_on_the_axis(videos, position, tracks,
                                                    ref_clip))
    if t0 is None:
        return 1
    # Only count now: what lies before In point is not missing. Where the
    # window covers only stretches that have audio, nothing appears here -- a
    # message about something that is not missing is noise.
    names = [track["name"] for track in tracks]
    starts = [b0 for b0, _ in audio_areas]
    ends = [b1 for _, b1 in audio_areas]

    def silence_report(missing, points, shape):
        """Report one side, front and back separately.

        Where all tracks are affected equally, one line for the worst case is
        enough. Only a track that stands out is named.
        """
        if max(missing) <= 1:
            return
        def sentence(how_much, point):
            return (T('Missing audio %s filled with silence%s')
                    % (shape % as_hms(point),
                       T(' -- an In or Out point saves the upload')
                       if how_much > 30 else ""))
        if max(missing) - min(missing) < 15:
            print("  %s" % sentence(max(missing), points[missing.index(max(missing))]))
            return
        for name, how_much, point in zip(names, missing, points):
            if how_much > 1:
                print("  %-20s %s" % (name, sentence(how_much, point)))

    silence_report([max(0.0, b - t0) for b in starts], starts, T('up to %s'))
    silence_report([max(0.0, t1 - b) for b in ends], ends,
                   T('from %s'))

    print(as_head(T('\nWRITING TRACKS TO THE AXIS')))
    for track in tracks:
        target = os.path.join(tmpdir, "axis_%s.wav" % safe_filename(track["name"]))
        drift = not args.no_drift and abs(track["b"] - 1.0) > 1e-7
        show_progress("%s" % track["name"], 0.0)
        place_track_on_axis(track["source"], target, track["a"], track["b"], t0, t1, drift)
        show_progress("%s" % track["name"], 1.0)
        print()
        track["axis"] = target
        track["drift"] = drift
        clock_drift = (track["b"] - 1.0) * 1e6
        print("    %s, %s%s" % (as_hms(sample_count(target) / float(SR)),
                                as_data_size(size_in_mb(target)),
                                T(', clock drift %s ppm taken out')
                                % decimal_text("%+.1f" % clock_drift)
                                if drift else T(', clock drift left in')))
    verify_alignment(tracks, t0, t1,
                     drift_allowed=not getattr(args, "no_drift", False))

    # Who speaks when, before anything is uploaded and before the audio
    # is processed: the axis stands now, so a separation can be placed
    # on it -- and only on the cameras that have a place, as in the
    # window: the segments of a file that sits nowhere land nowhere.
    args._speakers = separation_for_run(
        args, tracks, position, t0, t1,
        [ref_clip[0]] + [v for v, _e in videos
                         if v != ref_clip[0] and v in position])

    #--------------------------------------------------- Processing
    # --auphonic-done first, and on purpose. It names a folder: an
    # instruction about this run, not a mode. Read the other way round
    # the folder is never looked at and the run mixes the raw recordings.
    if getattr(args, "without_auphonic", False) and args.auphonic_done:
        print(as_warn(T('  --without-auphonic and --auphonic-done were '
                        'both given. The finished tracks win: there is '
                        'nothing left to send anywhere.')))
    if getattr(args, "without_auphonic", False) and not args.auphonic_done:
        return finish_without_auphonic(args, tracks, cameras, videos, tmpdir,
                                       position, t0, t1, ref_clip)
    if args.auphonic_done:
        # Already processed: the files are there. Saves a second upload and,
        # more to the point, the credit.
        folder = os.path.abspath(args.auphonic_done)
        print(as_head(T('\nALREADY PROCESSED')))
        print(T('  From %s') % folder)
        existing = [f for f in os.listdir(folder)
                     if os.path.splitext(f)[1].lower() in AUDIO_SUFFIXES]
        window = t1 - t0                       # what this run needs
        measured = full1 - full0        # the window without In point/Out point
        trimmed = abs(window - measured) > 0.001
        # Trimming leaves slack at both ends, so nothing is lost even where a
        # jingle was prepended. The return check finds the exact position
        # anyway and trims to the sample.
        MARGIN = 30.0
        shift = t0 - full0
        bad = []
        for track in tracks:
            best = max(existing, key=lambda f: similarity(
                track["name"], os.path.splitext(f)[0])) if existing else None
            quality = similarity(track["name"],
                             os.path.splitext(best)[0]) if best else 0.0
            if not best or quality < 0.6:
                print(T('    %-20s no file with a matching name') % track["name"])
                bad.append(track["name"])
                continue
            file_path = os.path.join(folder, best)
            length = sample_count(file_path) / float(SR)
            # The length may differ by a jingle but not by minutes, or
            # the file belongs to a different run. Two lengths qualify:
            # this run's window, and the measured one without In and Out
            # point, which is longer and gets trimmed.
            if abs(length - window) <= 60:
                track["done"] = file_path
                existing.remove(best)
                print(T('    %-20s <- %s  (%s, name similarity %s)')
                      % (track["name"], best, as_hms(length),
                         decimal_text("%.2f" % quality)))
                continue
            if trimmed and abs(length - measured) <= 60:
                # A prepended jingle lengthens the file; everything sits
                # further back by the same amount.
                front = shift + max(0.0, length - measured)
                target = os.path.join(tmpdir,
                                    "window_%s.wav" % safe_filename(track["name"]))
                place_track_on_axis(file_path, target, front - MARGIN, 1.0, 0.0,
                               window + 2 * MARGIN, drift=False)
                track["done"] = target
                track["edge"] = MARGIN
                existing.remove(best)
                print(T('    %-20s <- %s  (%s, trimmed to the time window, '
                        'name similarity %s)')
                      % (track["name"], best, as_hms(length),
                         decimal_text("%.2f" % quality)))
                continue
            print(T('    %-20s <- %s  BUT %s -- neither the time window '
                    '(%s) nor the\n    %-20s    whole measured range (%s). '
                    'This belongs to another run.')
                  % (track["name"], best, as_hms(length), as_hms(window), "",
                     as_hms(measured)))
            bad.append(track["name"])
        if bad:
            print(T('\n  Not usable: %s') % ", ".join(bad))
            print(T('  The files in the folder must be named after the '
                    'speakers and belong\n  to this run. Without the folder '
                    'it goes through auphonic.com again.'))
            return 1
        if args.dry_run:
            print(T('\n  (measuring only: nothing written)'))
            return 0
        if not verify_returned_tracks(tracks, t1 - t0, tmpdir):
            return 1
        gain, curve = normalise_loudness(
            tracks, args.lufs, tmpdir,
            find_master_file(folder, args.out, os.path.dirname(video_paths[0])),
            channels=mix_width(tracks))
        return distribute_tracks_to_cameras(
            args, tracks, cameras, videos, tmpdir, gain, position, t0,
            ref_clip, t1, curve)

    if args.dry_run and not args.auphonic_key:
        print(T('\n  (measuring only: without an API key it stops here)'))
        return 0
    key = api_key_from_anywhere(args)
    # The one place where a single recording really needs something
    # else. Only auphonic.com has two kinds of production, and a
    # multitrack preset holding one track is not what anybody wants, so
    # the preset follows the count and so does the production.
    alone = len(tracks) < 2
    try:
        preset, presetname = choose_preset(
            key, args.auphonic_preset, not alone, lufs=args.lufs,
            anyway=getattr(args, "anyway", False))
    except Exception as e:
        print(T('\nNo preset chosen: %s') % e)
        return 1
    folder = os.path.abspath(args.out) if args.out else os.path.dirname(
        os.path.abspath(video_paths[0]))
    print()
    try:
        if alone:
            one = run_single_production(
                tracks[0]["axis"], preset, presetname, key, folder,
                args.auphonic_wait, args.dry_run, title or 'Production')
            done = {tracks[0]["name"]: one} if one else {}
        else:
            done = run_multitrack_production(
                key, preset, title or 'Production', tracks, folder,
                args.auphonic_wait, args.dry_run, args.auphonic_resume)
    except Exception as e:
        print(as_bad(T('Processing failed: %s') % e))
        return 1
    for track in tracks:
        track["done"] = done.get(track["name"])
    missing = [track["name"] for track in tracks if not track.get("done")]
    if missing and not args.dry_run:
        print(T('\nEnded without a result: %s') % ", ".join(missing))
        return 1

    if args.dry_run:
        print(T('\n  (measuring only: nothing written)'))
        return 0

    if not verify_returned_tracks(tracks, t1 - t0, tmpdir):
        return 1
    gain, curve = normalise_loudness(
        tracks, args.lufs, tmpdir,
        find_master_file(folder, args.out, os.path.dirname(video_paths[0])),
        channels=mix_width(tracks))
    return distribute_tracks_to_cameras(
        args, tracks, cameras, videos, tmpdir, gain, position, t0, ref_clip,
        t1, curve=curve)


def check_written_file(target, items, n_camera, args, fps):
    """Measure in the finished file whether the new audio sits on the picture.

    Compared against the camera track using the overall mix, which
    carries the same voices as the camera microphone. A de-bled single
    track will not do: the other speakers are missing from it.
    """
    if args.no_camera_audio or not n_camera:
        return
    index_number = next((i for i, (name, _) in enumerate(items)
                   if name.startswith(MIX_TRACK_NAME)), 0)
    try:
        HOP, rate = 5.0, 4000
        duration = float(ffprobe_json(target).get("format", {}).get("duration") or 0)
        fresh, cam = decode_audio_tracks(
            target, rate, duration,
            T('Check: %s and camera track') % items[index_number][0],
            [index_number, len(items)])
        if not len(fresh) or not len(cam):
            print(T('  Check:           one of the two tracks is not in the '
                    'written file, so nothing was measured.'))
            return
        k, g = cross_correlate(envelope(cam, HOP, rate),
                               envelope(fresh, HOP, rate))
    except Exception as e:
        print(T('  Check:           not possible (%s)') % e)
        return
    # Whether the number means anything at all. Where the new track is
    # mostly silence there is nothing to line up against and the
    # arithmetic answers all the same. A check that cries wolf is worse
    # than none, because it is read as evidence.
    if g < WEAK_MATCH:
        print(T('  Check:           the two tracks cannot be compared '
                '(match %s, %s is the floor). This says nothing '
                'about the timing.')
              % (decimal_text("%.2f" % g), decimal_text("%.2f" % WEAK_MATCH)))
        return
    ms = k * HOP
    off = abs(ms) > 1000.0 / fps
    line = (T('  Check:           %s against the camera track %s ms '
              '(match %s)%s')
            % (items[index_number][0], decimal_text("%+.0f" % ms),
               decimal_text("%.2f" % g),
               T('   Caution: more than one frame') if off else ""))
    print(as_warn(line) if off else line)


def finish_camera_file(source, info, target, items, args, fps):
    """Everything that happens to a camera file once it is written.

    The colour, the camera's own QuickTime keys, its metadata, and the
    measurement of whether the new audio sits on the picture. Four
    things in a fixed order, the same on both paths.
    """
    check_colour_survived(source, target)
    # ffmpeg drops what it does not know. For iPhone recordings "logs"
    # holds the recording curve, which is how Resolve recognises Apple
    # Log. It is copied byte for byte from the source.
    try:
        after = copy_mov_atoms(source, target)
    except Exception as e:
        after = []
        print(T('  Camera atoms:    cannot be added (%s)') % str(e)[:60])
    if after:
        print(T('  Camera atoms:    %s added -- %s')
              % (", ".join(after),
                 log_curve_from_atom(_logs_atom_text(target)) or T('no text')))
    check_camera_metadata(source, target)
    check_data_tracks(source, target)
    check_written_file(target, items, len(info["audio"]), args, fps)
































def distribute_tracks_to_cameras(args, tracks, cameras, videos, tmpdir, gain,
              position, t0, ref_clip=None, t1=None, curve=None,
              segment_list=None):
    """Place the processed tracks onto the cameras.

    Without *segment_list* the speakers are worked out here: the tracks
    from auphonic.com are cleaner to measure than the raw ones.
    """
    step_begin("cameras")
    if segment_list is None:
        step_begin("speakers")
        segment_list = speakers_for_the_cut(args, tracks)
    names_every = [track["name"] for track in tracks]
    after_camera = ByFile()
    for track in tracks:
        if track.get("camera"):
            after_camera.setdefault(track["camera"], []).append(track)

    track_names = ByFile()    # output file -> names of its audio tracks
    offsets = ByFile()        # output file -> measured offset in seconds
    print(as_head(T('\nMIXING')))
    # Mixes of several tracks go out in two channels, single tracks in
    # as many as they were recorded with: the mix is what is delivered
    # and measured, the single track what is worked with in the edit.
    # One recording is the exception -- nothing to mix, nothing widened.
    wide = mix_width(tracks)
    full_mix = mix_tracks([track["ready"] for track in tracks],
                        os.path.join(tmpdir, "mix_full.wav"), gain,
                        curve, channels=wide)
    print(TN(wide, '  Full-Mix from %s tracks, %s channel',
             '  Full-Mix from %s tracks, %s channels')
          % (group_text(len(tracks)), group_text(wide)))

    # What is said and when, out of the finished mix. It runs beside the
    # cameras rather than in front of them: the words are needed only
    # when the cut is built at the end, and without them the wide shot
    # looks for the longest pause instead of the end of a sentence.
    heard = {}

    def listen_to_the_mix():
        """Write down the words of the mix, in a thread of its own."""
        words, _way = recognise_speech(
            full_mix, getattr(args, "speech_language", "") or "")
        heard["words"] = words or []

    listening = None
    if not getattr(args, "no_speech_recognition", False):
        listening = threading.Thread(target=listen_to_the_mix, daemon=True)
        listening.start()

    def heard_words():
        """Wait for the recognition and return what it heard."""
        if listening is not None:
            listening.join()
        return heard.get("words") or []

    single, in_stereo = {}, []
    for track in tracks:
        single[track["name"]] = mix_tracks(
            [track["ready"]],
            os.path.join(tmpdir, "single_%s.wav" % safe_filename(track["name"])),
            gain, curve)
        if kept_channels(single[track["name"]]) == 2:
            in_stereo.append(track["name"])
    if in_stereo:
        print(TN(len(in_stereo), '  %s stays in two channels',
                 '  %s stay in two channels') % ", ".join(in_stereo))
    # Filled from the keys of a ByFile and read back under abspath, so
    # it is one too. A plain dict here loses what the type settles: on
    # Windows the two spellings differ, the lookup raises, and every
    # camera with a track assigned goes unwritten without a word.
    camera_mix = ByFile()
    for file_path, own in after_camera.items():
        camera_mix[file_path] = mix_tracks(
            [track["ready"] for track in own],
            os.path.join(tmpdir, "mix_%s.wav"
                         % safe_filename(os.path.basename(file_path))), gain,
            curve, channels=mix_width(own))
        print(T('  %s: %s mixed together')
              % (os.path.basename(file_path),
                 " + ".join(track["name"] for track in own)))

    # Through path_key, both sides: a camera whose path arrives in
    # another shape than the same file in the video list loses the name
    # given here, writes itself under the bare file name, and then
    # misses its measured offset, which is kept under the file written.
    output_name = {path_key(cam["video"]): cam["name"] for cam in cameras}
    # The target names are settled before the threads start. Without a name
    # of its own a camera would write over an original -- its own or another
    # camera's, which a second thread may be reading at that moment -- and
    # two cameras with the same file name would write the same file at once.
    output_path, taken = {}, set()
    sources = set(os.path.abspath(_v).lower() for _v, _i in videos)
    for _v, _info in videos:
        _v = os.path.abspath(_v)
        stem = output_name.get(path_key(_v)) or os.path.splitext(
            os.path.basename(_v))[0]
        outdir = os.path.abspath(args.out) if args.out else os.path.dirname(_v)
        target = os.path.join(outdir, stem + ".mov")
        count = 1
        while target.lower() in sources or target.lower() in taken:
            count += 1
            tail = args.suffix or "_audio"
            target = os.path.join(outdir, "%s%s%s.mov"
                                  % (stem, tail,
                                     "" if count == 2 else "_%d" % count))
        taken.add(target.lower())
        output_path[_v] = (outdir, target)
    results, error = [], 0
    lengths = ByFile()    # output file -> running time delivered
    # An In or Out point is what makes the cameras carry a stretch
    # rather than the whole shoot. Without one they stay as they were,
    # so a run that sets no window writes exactly what it wrote before.
    window_s = (t1 - t0 if t1 is not None
                and ((getattr(args, "in_point", None) or "").strip()
                     or (getattr(args, "out_point", None) or "").strip())
                else None)
    # Programme time on the wall clock: the reference camera's clock
    # plus where the window starts. Every stamp is measured from here,
    # so they agree -- off each camera's own clock they did not, by
    # however much those disagreed.
    tc_start = None
    if ref_clip and ref_clip[1].get("tc") and t0 is not None:
        tc_start = parse_timecode(
            ref_clip[1]["tc"], max(1.0, ref_clip[1]["fps"])) + t0

    def one_camera(v, info, share):
        """Finish one camera: measure, write, verify.

        Runs in its own thread. Everything printed here collects in that
        thread's buffer and comes out in one piece once the file is
        done; progress goes to the shared bar instead.
        """
        v = os.path.abspath(v)
        own = after_camera.get(v, [])
        print(as_head(T('\nPROCESSING: %s') % os.path.basename(v)))
        items = []
        if own:
            items.append(('Mix ' + " + ".join(track["name"] for track in own)
                          if len(own) > 1 else own[0]["name"],
                          camera_mix[v]))
            if len(own) > 1:
                for track in own:
                    items.append((track["name"], single[track["name"]]))
            if set(track["name"] for track in own) != set(names_every):
                items.append((MIX_TRACK_NAME, full_mix))
        else:
            items.append((MIX_TRACK_NAME, full_mix))
            # And the recordings the mix was made of, each on a line of
            # its own, so the edit can reach one voice without importing
            # anything else. Only where no track has a camera at all --
            # with an assignment the wide shot gets the mix and nothing else.
            if (not after_camera and len(tracks) > 1
                    and not getattr(args, "no_single_tracks", False)):
                for track in tracks:
                    items.append((track["name"], single[track["name"]]))
        # Where the camera sits on the axis is already known from
        # building the time axis. Repeating it against a de-bled speaker
        # track would be worse: one speaker is left on it while the
        # camera microphone hears them all.
        if v not in position:
            print(T('  This camera could not be placed -- skipped'))
            return None
        a_cam, b_cam, st = position[v]
        a = -a_cam / b_cam - t0
        b = 1.0 / b_cam
        # Cross-check: the same offset, this time from the overall mix. That is
        # identical on every camera and holds the same voices as the camera
        # microphone. Where the two routes disagree something is wrong, and
        # that should show here rather than on playback.
        share.segment(0.0, 0.30)
        check = next((p for n, p in items
                      if n.startswith(MIX_TRACK_NAME)),
                     items[0][1])
        try:
            HOP, rate = 5.0, 4000
            env_video = video_envelope(v, HOP, rate)
            env_audio = envelope(decode_audio(check, rate=rate), HOP, rate)
            density = int(max(20, min(120, info["duration"] / 30.0)))
            a2, b2, st2 = align_envelopes(env_video, env_audio, HOP,
                                             sample_points=density,
                                             distance_s=30.0,
                                             points_off="audio",
                                             warn=os.path.basename(check))
            deviation = a2 - a
        except Exception as e:
            a2, st2, deviation = None, {}, None
            print(T('  Cross-check:     not possible (%s)') % e)
        fps = max(1.0, info["fps"])
        total = (b - 1.0) * info["duration"]
        uncertainty = st.get("ppm_error", 0.0) / 1e6 * info["duration"]
        threshold = max(0.010, 0.5 / fps)
        drift = (not args.no_drift
                 and abs(total) > 4 * uncertainty and abs(total) > threshold
                 and abs(st.get("ppm", 0.0)) < 500 and info["duration"] >= 120)
        print(T('  Offset:          %s   (from the camera comparison)') % as_hms(a))
        if a2 is not None:
            serious = abs(deviation) > 1.0 / fps
            print(T('  Cross-check:     %s from the Full-Mix, deviation '
                    '%s ms (%s of %s points)%s')
                  % (as_hms(a2),
                     decimal_text("%+.0f" % (deviation * 1000.0)),
                     group_text(st2.get("points", 0)),
                     group_text(st2.get("candidates", 0)),
                     T('   Caution: more than one frame') if serious else ""))
        # The reference camera is what the others were measured
        # against, so there is nothing here that was measured. The line
        # of noughts it used to print -- "+0.00 ppm (+/- 0.00), 0 of 0
        # points" -- read like a measurement and was none.
        if ref_clip and path_key(ref_clip[0]) == path_key(v):
            print(T('  Clock drift:     nothing measured -- this is the '
                    'reference the others are held against'))
        else:
            print(T('  Clock drift:     %s ppm (+/- %s), residual spread '
                    '%s ms, %s of %s points')
                  % (decimal_text("%+.2f" % ((b - 1.0) * 1e6)),
                     decimal_text("%.2f" % st.get("ppm_error", 0.0)),
                     decimal_text("%.1f" % st.get("spread_ms", 0.0)),
                     group_text(st.get("points", 0)),
                     group_text(st.get("candidates", 0) or 0)))
            print(T('  Drift over the running time: %s s = %s frames  -->  %s')
                  % (decimal_text("%+.3f" % total),
                     decimal_text("%.1f" % (abs(total) * fps)),
                     T('is actively taken out') if drift
                     else T('is left in')))
        print()
        outdir, target = output_path[v]
        os.makedirs(outdir, exist_ok=True)
        # What lies before the In point and after the Out point appears
        # in no cut, and on a long shoot it is the bulk of the file. So
        # the camera is written from the key frame before the window to
        # a margin past its end; without a window nothing is cut.
        cut_at, keep_s = 0.0, None
        if window_s is not None:
            cut_at, keep_s = camera_window_cut(v, info["duration"], a,
                                               window_s)
            a += cut_at
        # Where this file's first frame sits on the wall clock. a is
        # the measured place of that frame in programme time, so this
        # is the one number every camera's stamp comes from.
        at_s = None if tc_start is None else tc_start + a
        share.segment(0.30, 0.85)
        try:
            write_camera_file(v, info, items, target, a, b, drift, args,
                              cut_at=cut_at, keep_s=keep_s, at_s=at_s)
        except Exception as e:
            print(as_bad(T('  Error while writing: %s') % e))
            return None
        track_names = [name for name, _ in items]
        for i, (name, _) in enumerate(items, 1):
            print(T('  Audio track %d:   %s') % (i, name))
        if not args.no_camera_audio and info["audio"]:
            print(T('  Audio track %d:   %s') % (len(items) + 1,
                                              args.name_camera))
        stamp = camera_stamp(info, cut_at, at_s)
        if stamp:
            print("  Timecode:        %s" % stamp)
        if keep_s:
            print(T('  Time window:     %s of %s written, from %s of the '
                    'camera') % (as_hms(keep_s), as_hms(info["duration"]),
                                 as_hms(cut_at)))
        share.segment(0.85, 1.0)
        finish_camera_file(v, info, target, items, args, fps)
        return target, track_names, a, (keep_s or info["duration"])

    # The expensive part is the cross-check, and that only computes. ffmpeg
    # merely copies the picture and waits on the disk. Together they saturate
    # a machine only with several files running at once.
    how_many = getattr(args, "parallel", 0) or min(
        len(videos), max(1, min(4, how_many_processors() // 2)))
    how_many = max(1, min(how_many, len(videos)))
    progress_bar = SharedProgressBar(T('Processing'), len(videos))

    def one(v, info):
        ident = threading.get_ident()
        THREAD_BUFFER[ident] = []
        THREAD_SHARE[ident] = Share(progress_bar, v)
        try:
            return one_camera(os.path.abspath(v), info, THREAD_SHARE[ident])
        except Exception as e:
            print(T('\n  Stopped: %s') % e)
            return None
        finally:
            THREAD_SHARE[ident].report(1.0)
            THREAD_SHARE.pop(ident, None)
            one_camera.texts[v] = "".join(THREAD_BUFFER.pop(ident, []))

    one_camera.texts = {}
    old_off = sys.stdout
    progress_bar.stream = old_off
    sys.stdout = ThreadOutput(old_off)
    try:
        with futures.ThreadPoolExecutor(max_workers=how_many) as pool:
            job = {pool.submit(one, v, info): v for v, info in videos}
            for done_future in futures.as_completed(job):
                v = job[done_future]
                sys.stdout.write("\n" + one_camera.texts.get(v, ""))
                what = done_future.result()
                if what is None:
                    error += 1
                    continue
                target, names, offset, delivered = what
                track_names[target] = names
                offsets[target] = offset   # camera position in the window
                lengths[target] = delivered
                results.append(target)
    finally:
        sys.stdout = old_off
    progress_bar.stop()
    # Back in file order, not in the order of completion.
    order = [os.path.abspath(x) for x, _ in videos]
    results.sort(key=lambda path: order.index(os.path.abspath(path))
                    if os.path.abspath(path) in order else len(order))

    # --- keep the finished tracks, not only hidden inside the videos
    folder = os.path.abspath(args.out) if args.out else os.path.dirname(
        os.path.abspath(videos[0][0]))
    cache = tracks_folder(folder)
    print(as_head(T('\nSAVING TRACKS')))
    # The stored tracks belong to programme time, not to a camera, so
    # their timecode is written at the rate the Timeline runs at.
    tc_fps = max(1.0, timeline_frame_rate(args, videos, ref_clip))
    stored = []
    single_files = {}      # speaker name -> stored WAV
    tc_name = ("_" + timecode_string(tc_start, tc_fps).replace(":", "-"))\
        if tc_start is not None else ""
    for name, source in ([(track["name"], single[track["name"]]) for track in tracks]
                         + [(MIX_TRACK_NAME, full_mix)]):
        target = os.path.join(cache,
                            "final_%s%s.wav" % (safe_filename(name), tc_name))
        show_progress(T('Saving %s') % name, 0.0)
        command = ["ffmpeg", "-v", "error", "-i", source, "-c:a", "copy"]
        if tc_start is not None:
            command += ["-write_bext", "1", "-metadata",
                       "time_reference=%d" % int(round(tc_start * SR))]
        shell_quote(command + ["-y", target])
        if tc_start is not None:
            # Resolve reads bext; Premiere and Media Composer read iXML.
            try:
                append_ixml(target, build_ixml(
                    name, int(round(tc_start * SR)), tc_fps, 24, 1,
                    is_drop_frame(ref_clip[1].get("tc") if ref_clip else None)))
            except Exception as e:
                print(T('  iXML for %s not written: %s')
                      % (os.path.basename(target), e))
        stored.append(target)
        single_files[name] = target
        show_progress(T('Saving %s') % name, 1.0)
        print("\r  %-24s %s%s" % (os.path.basename(target),
                                  as_hms(sample_count(target) / float(SR)),
                                  " " * 20))
    if tc_start is not None:
        print(T('  Timecode %s written as bext and iXML (reference: %s)')
              % (timecode_string(tc_start, tc_fps),
                 os.path.basename(ref_clip[0])))

    if results:
        print(as_head(T('\nRESULT')))
        for path in results:
            print("  %s" % path)
        for path in stored:
            print("  %s" % path)
        # What is in the folder is no longer the whole shoot, and that is
        # worth a sentence: whoever wants more of it than the window
        # holds sets the In and Out point wider and runs again.
        if window_s is not None and lengths:
            print(T('  The cameras carry the time window and a second at '
                    'each end: %s written for %s of the %s recorded.')
                  % (as_data_size(sum(size_in_mb(p) for p in results)),
                     as_hms(sum(lengths.values())),
                     as_hms(sum(i["duration"] for _v, i in videos))))

    # The last stage: the cut list, the handover, the result. The bar
    # lists it, so it is announced here too.
    step_begin("result")
    cut, segment_list = write_cut_list(
        args, segment_list, tracks, cameras, videos, folder, tc_start,
        ref_clip, t1 - t0 if t1 is not None else 0,
        words=heard_words(), sound_source=single_files.get(MIX_TRACK_NAME, ""))
    # Who does the asking. Said, not acted on: the order is what the
    # measurement supports, and a name in the interface is a person's
    # decision.
    asking = who_asks(segment_list, heard_words())
    for line in (roles_report(asking, segment_list)
                 + voice_names_report(asking)):
        print(line)
    if not getattr(args, "no_transcript_file", False) and heard_words():
        print(as_head(T('\nTRANSCRIPT')))
        for path in write_transcript_files(
                folder, safe_filename(args.production or 'Production'),
                heard_words(), segment_list):
            print("  %s" % path)
    # Content and wide shot, and nothing else. The comparison exists to
    # show what a cut between two cameras looks like, so a file that is
    # never cut against them does not belong in it: an 18-second jingle
    # raised a caution about 357 steps of brightness (31.8.2026).
    placed_cameras = {path_key(k) for k in (position or {})}
    at_the_edges = set(path_key(p) for p in
                       (getattr(args, "intro", None), getattr(args, "outro", None))
                       if p)

    def cut_against_the_others(cam):
        where = path_key(cam.get("video") or "")
        return where in placed_cameras and where not in at_the_edges

    colours = []
    if not getattr(args, "no_metrics", False):
        made = (results if len(results) == len(cameras)
                else [cam.get("video") for cam in cameras])
        try:
            colours = report_picture_comparison(
                [{"track": cam.get("name"), "file": p}
                 for cam, p in zip(cameras, made)
                 if cut_against_the_others(cam)])
        except Exception as e:
            print(T('  Colour comparison not possible: %s') % e)
        print(as_head(T('\nMETRICS')))
        target = write_metrics_csv(
            os.path.join(folder, "%s_metrics.csv"
                         % safe_filename(args.production or 'Production')),
            tracks, cut, segment_list, cameras, args, colours, gain)
        if target:
            print("  %s" % target)
    write_handover(args, tracks, cameras, videos, folder, tc_start,
                      ref_clip, results, cut, segment_list,
                      t1 - t0 if t1 is not None else 0, track_names,
                      single_files, offsets, lengths, words=heard_words(),
                      unplaceable=[cam["video"] for cam in cameras
                                   if path_key(cam["video"])
                                   not in placed_cameras])
    shutil.rmtree(tmpdir, ignore_errors=True)
    return 1 if error else 0


def audible_range(file_path, rate=8000, block=0.05, below_db=40.0):
    """Return where audible sound starts and ends in a file.

    Audible sound, not file length: a jingle can sit in a longer file
    with silence at the end, and what counts is when it stops. The
    threshold sits 40 dB below the loudest point of the file itself, a
    fixed value being silent throughout on a quietly mastered jingle.
    Returns (start, end) in seconds, or (None, None).
    """
    try:
        x = decode_audio(file_path, rate=rate)
    except Exception:
        return None, None
    if x is None or len(x) < rate // 4:
        return None, None
    nb = max(1, int(block * rate))
    count = len(x) // nb
    if count < 2:
        return None, None
    level = np.sqrt((np.asarray(x[:count * nb], dtype=np.float64)
                     .reshape(-1, nb) ** 2).mean(1))
    highest = float(level.max())
    if highest <= 0:
        return None, None
    loud = np.where(level > highest * (10 ** (-below_db / 20.0)))[0]
    if not len(loud):
        return None, None
    return (float(loud[0]) * block, float(loud[-1] + 1) * block)


def _intro_outro_entry(file_path):
    """Build the intro or outro entry for the handover file."""
    if not file_path or not os.path.exists(file_path):
        return None
    try:
        info = video_facts(file_path)
    except Exception:
        return None
    duration = round(float(info.get("duration") or 0.0), 3)
    has_audio = bool(info.get("audio"))
    audio_from, audio_until = (audible_range(file_path) if has_audio else (None, None))
    return {"source": os.path.abspath(file_path),
            "duration": duration,
            "has_audio": has_audio,
            # When the audible sound starts and stops. The position follows
            # that, not the file length.
            "audio_from": round(audio_from, 3) if audio_from is not None else None,
            "audio_to": round(audio_until, 3) if audio_until is not None else None}


# =====================================================================
#  Metrics and colour comparison
#  -----------------------------
#  What was measured at the end of an episode belongs in a file, not
#  only in the log, which the next run overwrites. Over months it
#  shows whether a camera increasingly looks unlike the others,
#  whether a recorder is drifting, or whether crosstalk rose with a
#  new setup.
# =====================================================================

def measure_picture_levels(file_path, spots=5, t0=0.0, t1=None):
    """Measure brightness and colour balance of a camera file from samples.

    Returns {"y": ..., "u": ..., "v": ..., "sat": ...} or None. Y is
    brightness, U and V are the colour differences -- 128 is neutral, above
    and below is the cast. Measured on a few frames, which is enough to
    compare cameras without reading the whole file.
    """
    if t1 is None or t1 <= t0:
        try:
            t1 = float(ffprobe_json(file_path).get("format", {}).get("duration") or 0.0)
        except Exception:
            t1 = 0.0
    if t1 <= t0:
        return None
    points = [t0 + (t1 - t0) * (k + 0.5) / spots for k in range(spots)]
    values = {"y": [], "u": [], "v": [], "sat": []}
    for time in points:
        try:
            p = subprocess.run(
                ["ffmpeg", "-v", "error", "-ss", "%.3f" % time, "-i", file_path,
                 "-frames:v", "1", "-vf", "signalstats,metadata=print:file=-",
                 "-f", "null", "-"], capture_output=True, timeout=120)
        except Exception:
            continue
        text = p.stdout.decode("utf-8", "replace")
        for api_key, label in (("y", "YAVG"), ("u", "UAVG"),
                                  ("v", "VAVG"), ("sat", "SATAVG")):
            hit = re.search(r"signalstats\.%s=([\d.]+)" % label, text)
            if hit:
                values[api_key].append(float(hit.group(1)))
    if not values["y"]:
        return None
    return dict((k, sum(v) / len(v)) for k, v in values.items() if v)


def compare_picture_levels(cameras, t0=0.0, t1=None):
    """Report how far the cameras sit apart in colour.

    Each camera is compared with the average of all, not with a target.
    Which brightness is right is for the grade to decide; what matters here
    is the distance between cameras, because that shows in the edit as soon
    as it cuts.

    Returns a list of (name, values, deviations) and the averages.
    """
    measured = []
    for cam in cameras:
        file_path = cam.get("file") or cam.get("source")
        if not file_path or not os.path.exists(file_path):
            continue
        values = measure_picture_levels(file_path, t0=t0, t1=t1)
        if values:
            measured.append((cam.get("track") or cam.get("camera") or
                             os.path.basename(file_path), values))
    if len(measured) < 2:
        return measured, None
    middle = {}
    for api_key in ("y", "u", "v", "sat"):
        every = [values[api_key] for _n, values in measured if api_key in values]
        if every:
            middle[api_key] = sum(every) / len(every)
    return measured, middle


def report_picture_comparison(cameras, t0=0.0, t1=None):
    """Write the colour comparison to the log. Returns the measurements."""
    measured, middle = compare_picture_levels(cameras, t0, t1)
    if not measured:
        return []
    print(as_head(T('\nCAMERA COLOUR COMPARISON')))
    print("  %-24s %8s %8s %8s   %s"
          % (T('Camera'), T('Bright.'), T('Colour U'), T('Colour V'),
             T('Distance to mean')))
    lines = []
    for name, values in measured:
        if middle:
            dy = values.get("y", 0) - middle.get("y", 0)
            du = values.get("u", 0) - middle.get("u", 0)
            dv = values.get("v", 0) - middle.get("v", 0)
            distance = "%+6.1f  %+5.1f  %+5.1f" % (dy, du, dv)
        else:
            dy = du = dv = 0.0
            distance = T('-- only one camera')
        print("  %-24s %8.1f %8.1f %8.1f   %s"
              % (name[:24], values.get("y", 0), values.get("u", 0), values.get("v", 0),
                 distance))
        lines.append((name, values, (dy, du, dv)))
    if middle:
        spread = max(abs(line[2][0]) for line in lines)
        if spread > 12:
            print(as_warn(T('  Caution: %s steps of brightness '
                            'difference -- visible when switching.')
                          % decimal_text("%.0f" % spread)))
        else:
            print(T('  The cameras lie close together (at most %s steps '
                    'of brightness).') % decimal_text("%.0f" % spread))
    return lines


def preview_handover(state):
    """Read the run's handover for the preview, or answer None.

    A finished run beats whatever the window worked out for itself: its
    tracks lie on one axis and auphonic.com has de-bled them. So its
    measurement is the reference and the one taken from the raw tracks
    is dropped, not shown beside it -- and nobody is left waiting to be
    measured either, because the run measured every track it had.
    """
    d, js = None, state.get("resolve_json")
    state["preview_from"] = None
    if js:
        try:
            with open(js, encoding="utf-8") as f:
                d = json.load(f)
            state["preview_from"] = handover_mark(js)
        except (OSError, ValueError):
            d = None
    state["cut_basis"] = (("auphonic" if state.get("run_auphonic")
                           else "run") if d is not None else "measured")
    if d is not None:
        state["tracks_left"] = []
        state["stat_measured"] = "run"
    return d


def preview_out_of_date(state, multitrack_on):
    """Whether the preview has to be worked out from the handover again.

    It appears by itself when a run leaves one behind, and it is stale
    again when the same file is rewritten: "Create Resolve project"
    works the cut out from the numbers set now and writes it back under
    the name it had.
    """
    if state.get("running") or not multitrack_on:
        return False
    js = state.get("resolve_json")
    return bool(js) and (not state.get("statistics")
                         or handover_mark(js) != state.get("preview_from"))


def handover_mark(file_path):
    """What tells one state of a handover file from the next.

    The path alone does not: pressing "Create Resolve project" works the
    cut out again from the numbers now set and writes the same file
    again, and a preview that went by the name would keep showing the
    cut from before.
    """
    try:
        s = os.stat(file_path)
        return (os.path.abspath(file_path), s.st_mtime_ns, s.st_size)
    except OSError:
        return None


def handover_over_this_material(d, ours):
    """Whether this handover names exactly the cameras in hand.

    One lying in a result folder may be days old, from another
    production or from a round with other cameras: measured 30.8.2026,
    a cut built out of a four-day-old handover looked exactly like a
    fresh one. A camera too few is as wrong as a camera too many, so
    the two lists have to be the same list.
    """
    mine = set(path_key(p) for p in ours or () if p)
    theirs = set(path_key(c.get("source") or c.get("camera") or "")
                 for c in (d.get("cameras") or [])
                 if (c.get("source") or c.get("camera")))
    return bool(theirs) and theirs == mine


def find_handover_file(*places, deeper=False, ours=None):
    """Find the newest usable ..._resolve.json in these folders.

    *deeper* includes subfolders: the result of an earlier run often sits in
    a subfolder next to the raw material. *ours* is the material in hand;
    a handover naming anything else is passed over.
    A file an older version wrote is skipped rather than returned: the
    caller would read it, find none of the keys it expects and report the
    material as empty instead of the file as old.
    """
    look = []
    for place in places:
        if not place or not os.path.isdir(place):
            continue
        place = os.path.abspath(place)
        if place not in look:
            look.append(place)
        if not deeper:
            continue
        try:
            for name in sorted(os.listdir(place)):
                below = os.path.join(place, name)
                if os.path.isdir(below) and not name.startswith("."):
                    if below not in look:
                        look.append(below)
        except OSError:
            pass
    hit = []
    for place in look:
        try:
            names = os.listdir(place)
        except OSError:
            continue
        for name in names:
            if name.lower().endswith("_resolve.json"):
                file_path = os.path.join(place, name)
                try:
                    with open(file_path, encoding="utf-8") as f:
                        d = json.load(f)
                    if format_complaint(d):
                        continue
                    if ours is not None and not handover_over_this_material(
                            d, ours):
                        continue
                    hit.append((os.path.getmtime(file_path), file_path))
                except (OSError, ValueError):
                    pass
    return max(hit)[1] if hit else None


def colours_pick(dark):
    """Fill COLOURS with the set this desktop asks for.

    Refilled in place rather than replaced: every module and every
    style sheet holds on to this one dictionary, and a new object
    would leave all of them reading the old one. Called again when the
    desktop switches while the program runs.
    """
    COLOURS.clear()
    COLOURS.update(COLOURS_DARK if dark else COLOURS_LIGHT)
    ON_DARK[0] = bool(dark)


def sheet_recoloured(sheet, dark):
    """Return one style sheet with the colours of the other set in it.

    The two palettes carry the same roles under the same names, so a
    colour is found by looking up which role holds that value in the
    set being left and putting the value the same role holds in the
    set being entered. No two roles share a value and no value occurs
    in both sets, so a swap cannot be applied twice.

    A colour that stands in neither set is left where it is: the black
    behind a video is not a role, it is the colour a picture is shown
    against, and it is that in both schemes.
    """
    leaving = COLOURS_LIGHT if dark else COLOURS_DARK
    entering = COLOURS_DARK if dark else COLOURS_LIGHT
    for role, value in leaving.items():
        if value in sheet:
            sheet = sheet.replace(value, entering[role])
    return sheet


def app_style_set(app):
    """Put the palette into the style sheet of the whole program.

    Its own function so it can be set again when the desktop
    switches between light and dark, and out here rather than inside
    the window, which is long enough without it.
    """
    app.setStyleSheet("""
    QGroupBox {
        border: 1px solid %(frame)s; border-radius: 6px;
        /* The top margin is half the height of the heading, so the
           line runs through the middle of the text. */
        margin-top: 10px; padding-top: 14px; background: %(box)s;
    }
    QGroupBox::title {
        subcontrol-origin: margin; subcontrol-position: top left;
        left: 12px; top: 2px; padding: 0 8px; background: %(box)s;
        color: %(heading)s; font-weight: bold;
    }
    QTabWidget::pane {
        border: 1px solid %(frame)s; border-radius: 6px; top: -1px;
        background: %(sheet)s;
    }
    QTabWidget::tab-bar { alignment: left; left: 6px; }
    QTabBar::tab {
        background: %(head)s; color: %(quiet)s;
        border: 1px solid %(frame)s; border-bottom: none;
        border-top-left-radius: 6px; border-top-right-radius: 6px;
        padding: 8px 22px; margin-right: 3px; font-weight: bold;
    }
    QTabBar::tab:selected { background: %(heading)s; color: %(sheet)s; }
    QTabBar::tab:hover:!selected { background: %(stripe)s; }
    QHeaderView::section {
        background: %(head)s; color: %(heading)s; font-weight: bold;
        border: 0px; border-bottom: 1px solid %(frame)s; padding: 4px;
    }
    QTableWidget, QTreeView, QTextEdit, QListWidget {
        background: %(sheet)s; alternate-background-color: %(head)s;
        color: %(text)s;
    }
""" % {k: COLOURS[k] for k in ("frame", "box", "heading", "head",
                              "quiet", "sheet", "stripe", "text")})


def styles_follow_scheme(app, dark):
    """Recolour every widget that styled itself, and say how many.

    What a widget wrote into its own style sheet when it was built is
    out of reach of the style sheet of the whole program: setting that
    again leaves those rows in the colours of the scheme they were
    born in. Measured on 24.8.2026 with the interview project open: 58
    widgets carry a style sheet of their own, every one of them names
    a colour, and a desktop switched to dark left 50 of them light.

    Which ones they are does not have to be remembered, because Qt
    knows: a widget with a style sheet of its own is one whose
    ``styleSheet()`` is not empty. So nothing has to be marked while
    the interface is built, and a place that writes a colour without
    telling anybody is reached as well.
    """
    changed = 0
    for widget in app.allWidgets():
        try:
            sheet = widget.styleSheet()
        except RuntimeError:
            continue                  # gone while we were walking
        if not sheet:
            continue
        fresh = sheet_recoloured(sheet, dark)
        if fresh == sheet:
            continue
        try:
            widget.setStyleSheet(fresh)
        except RuntimeError:
            continue
        changed += 1
    return changed


def clip_colour_rgb(name):
    """Return the RGB approximation of a clip colour for this background."""
    exception = (CLIP_COLOURS_RGB_DARK if ON_DARK[0]
                else CLIP_COLOURS_RGB_LIGHT)
    if name in exception:
        return exception[name]
    return CLIP_COLOURS_RGB.get(name, "#888888")


def mix_file_from_handover(d):
    """Return the file carrying the overall mix.

    Preferably the separate file, which is unambiguous. Otherwise the wide
    shot, where the mix is the first audio track. Otherwise any camera with
    a track of that name.
    """
    for name, file_path in (d.get("audio_files") or {}).items():
        if "full" in name.lower() and file_path and os.path.exists(file_path):
            return file_path, T('stored file %s') % os.path.basename(file_path)
    for cam in (d.get("cameras") or []):
        if cam.get("wide") and cam.get("file") and os.path.exists(cam["file"]):
            return cam["file"], (T('wide shot %s, the mix is its first audio '
                                 'track') % cam["camera"])
    for cam in (d.get("cameras") or []):
        names = [n.lower() for n in (cam.get("audio_tracks") or [])]
        if any("full" in n for n in names) and os.path.exists(
                cam.get("file") or ""):
            idx = [i for i, n in enumerate(names, 1) if "full" in n][0]
            return cam["file"], (T('%s, audio track %d') % (cam["camera"], idx))
    return None, ""


def first_and_last_word(d):
    """Return when the first word falls and when the last one ends.

    Taken from the speaker statistics already in the handover file -- the
    same source the camera cut was computed from. Returns (first, last) in
    seconds from the start of the timeline, or (None, None) without
    statistics.
    """
    starts, ends = [], []
    for speaker in (d.get("speakers") or []):
        for a, b in (speaker.get("sections") or []):
            starts.append(float(a))
            ends.append(float(b))
    if not starts:
        return None, None
    return min(starts), max(ends)


def _meeting_point(entry, kind):
    """Return the point in the clip that should meet the word.

    For the intro that is the end of its audible audio, where the first word
    should start. For the outro the start of its audio, by which the last
    word should have died away. A clip without audio uses its end for the
    intro and its start for the outro.

    Nothing is cut: both clips keep their full length and only their
    position moves. The picture overlap is intended -- the dissolve sits
    in it, and where exactly is decided in Resolve.
    """
    entry = entry or {}
    duration = float(entry.get("duration") or 0.0)
    if kind == "intro":
        value = entry.get("audio_to")
        return float(value) if value is not None else duration
    value = entry.get("audio_from")
    return float(value) if value is not None else 0.0


def lead_in_offset(mp, tl, d, clips, fps, origin):
    """Place intro and outro on the second video and audio track.

    The intro sits over the beginning: its end falls on the first spoken
    word and its audio continues on its own track under the first words. The
    outro starts where the last word ends.

    The scripting interface cannot make the dissolve -- it knows no
    transitions. So the intro lies *over* the content rather than beside it:
    one drag on the clip corner and the dissolve is there.

    Returns by how many frames the content has to move back.
    """
    intro = d.get("intro")
    if not intro:
        return 0
    word0, _word1 = first_and_last_word(d)
    W = word0 if word0 is not None else 0.0
    # The content moves only as far as the intro reaches past the start --
    # measured at the point its audio stops, not at its file length. Where
    # someone starts speaking late, nothing moves.
    return seconds_to_frames(max(0.0, _meeting_point(intro, "intro") - W), fps)


HINT_MULTICAM = ('\n  To convert: in the media pool right-click "%s '
                 'Multicam" >\n  "Convert Timeline to Multicam Clip" > '
                 '"Use Source Audio Channels".\n  One way only -- but a '
                 'new run rebuilds the Timeline at any time.\n  Angles:%s\n '
                 ' Everything else -- audio choice, colour groups, '
                 'framing -- is in the\n  manual, docs/resolve.md.\n')



# How the command line switch is named and how the field behind it. All others
# are named alike, with an underscore instead of a hyphen.
SLIDER_TO_DEST = {"edit-change-delay": "delay"}


def cut_slider_defaults():
    """Return the camera cut sliders with their defaults.

    Derived from CUT_FIELDS so there is a single source. The same number in
    three places drifts apart, and then the same data yields a different cut
    depending on which path produced it.
    """
    out = []
    for api_key, _b, default_value, _e, _k, _l in CUT_FIELDS:
        field = SLIDER_TO_DEST.get(api_key, api_key.replace("-", "_"))
        try:
            out.append(("--" + api_key, field, float(default_value)))
        except ValueError:
            continue
    # None like the switch itself: no --lufs in the stored call means the
    # run took the loudness from the source files, not that it took -16.
    out.append(("--lufs", "lufs", None))
    # And two numbers the run takes that the window has no field for.
    # Out of CUT_FIELDS alone they are not recovered, and the rules then
    # fall back to their own default -- "--reaction-gap 8" came back
    # from the stored call as 3.0.
    out.append(("--reaction-gap", "reaction_gap", 3.0))
    out.append(("--reaction-hold", "reaction_hold", 0.7))
    return out


def _sliders_from_command_line(call, production):
    """Recover the sliders from the stored command line.

    A stand-in for the command line, complete enough for write_cut_list.
    """
    class Sliders(object):
        pass
    e = Sliders()
    e.production = production
    e.no_wide_edges = "--no-wide-edges" in (call or [])
    # Every --wide-shot in the stored call, not only the first: the mark
    # may stand on several cameras. Without this the button built the
    # cut again with no wide shot at all, while the window above still
    # showed one marked.
    e.wide_shot = [(call or [])[i + 1] for i, x in enumerate(call or [])
                   if x == "--wide-shot" and i + 1 < len(call or [])]
    # And the file saying which voice was heard on which camera. Without
    # it every separately heard voice falls back to the wide shot after
    # the button, while the window above still shows it on its own.
    for switch in ("--assign", "--speakers-from"):
        value = ""
        if call and switch in call:
            i = call.index(switch)
            if i + 1 < len(call):
                value = call[i + 1]
        setattr(e, switch[2:].replace("-", "_"), value)
    for switch, field, default_value in cut_slider_defaults():
        value = default_value
        if call and switch in call:
            i = call.index(switch)
            if i + 1 < len(call):
                try:
                    value = float(call[i + 1])
                except ValueError:
                    pass
        setattr(e, field, value)
    for switch, _caption, default_value, values, _k, _l in CUT_CHOICES:
        value = default_value
        if call and "--" + switch in call:
            i = call.index("--" + switch)
            if i + 1 < len(call) and call[i + 1] in values:
                value = call[i + 1]
        setattr(e, switch.replace("-", "_"), value)
    return e


def _read_project_file(folder):
    for file_path in sorted(glob.glob(os.path.join(folder,
                                              "videopodcast-magic_*.json"))):
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            continue
    return {}


def refresh_cut_list(d, file_path):
    """Check the cut list is still valid before building.

    Who speaks when is in the handover file already, so turning the cut
    values afterwards costs no run and no measurement. What only a new
    run can mend: In point or Out point changed since, and then the
    audio inside the videos belongs to a different window. The return
    value is that reason as text.
    """
    folder = os.path.dirname(os.path.abspath(file_path))
    project = _read_project_file(folder)
    speakers = [(x.get("name") or "", [tuple(v) for v in
                                       (x.get("sections") or [])])
                for x in (d.get("speakers") or [])]
    if not speakers or not project or d.get("start_s") is None:
        return None
    fps = max(1.0, float(d.get("fps_measured") or d.get("fps") or 30.0))
    call = project.get("call") or []

    # Does the project file now hold a different time window from the handover?
    # Then the audio files no longer match it.
    def tc_value(switch):
        if switch not in call:
            return None
        i = call.index(switch)
        if i + 1 >= len(call):
            return None
        try:
            return parse_timecode(call[i + 1], fps)
        except Exception:
            return None
    in_point, out_point = tc_value("--in-point"), tc_value("--out-point")

    def then(key):
        """The window the existing files were made with, in seconds."""
        raw = d.get(key)
        if not raw:
            return None
        try:
            return parse_timecode(raw, fps)
        except Exception:
            return None

    made_in, made_out = then("in_point"), then("out_point")
    # Both complaints hold the setting against the window the handover
    # was made with, and both stay silent where the handover does not
    # carry it -- older files do not, and neither does any run without
    # one. Only the complaints fall silent: the cut list is worked out
    # again either way, which is the whole point of pressing the button.
    # The older test held the In point against the zero of the axis and
    # refused every window that did not start at the first camera.
    if (in_point is not None and made_in is not None
            and abs(in_point - made_in) > 0.5):
        return (T('In point is now %s, but the existing files belong to %s.\n '
                  ' The audio in the videos is cut to the old window -- '
                  'press Start\n  above again.')
                % (timecode_string(in_point, fps),
                   timecode_string(made_in, fps)))
    # The old window's length, and only where both its ends are written
    # down. length_s is no substitute: that is the axis, the whole of
    # the material, and holding a window against it makes a window that
    # never changed look 4 1/2 minutes too short.
    length = ((made_out - made_in)
              if made_in is not None and made_out is not None else 0.0)
    if (in_point is not None and out_point is not None
            and length and abs((out_point - in_point) - length) > 0.5):
        return (T('Out point is now %s; the window would be %s long, the '
                  'existing\n  files are %s -- press Start above again.') % (timecode_string(out_point, fps), as_hms(out_point - in_point),
                            as_hms(length)))

    print(T('\n  REFRESH THE CUT LIST'))
    # The sliders come from the interface where they were sent along, otherwise
    # from the project file. Otherwise the button would carry on with the
    # values of the last run while something else is set above.
    command_line = [a for a in sys.argv[1:]]
    own_measure = any(a.startswith("--wide-")
                 or a in ("--min-edit-duration", "--edit-change-delay")
                 for a in command_line)
    settings = _sliders_from_command_line(command_line + call,
                                          d.get("production"))
    if own_measure:
        settings.no_wide_edges = "--no-wide-edges" in command_line
    cameras = [{"video": cam["source"], "name": cam["camera"]}
               for cam in (d.get("cameras") or []) if cam.get("source")]
    videos = [(cam["video"], None) for cam in cameras]
    tracks = [{"name": n, "camera": cam["source"]}
              for cam in (d.get("cameras") or [])
              for n in (cam.get("speakers") or [])]
    ref_clip = (cameras[0]["video"] if cameras else "",
                {"fps": fps, "tc": d.get("start_tc")})
    # The handover file carries what was said and where the sound is:
    # the cut points come from those two, not from the clock.
    cut, segs = write_cut_list(
        settings, speakers, tracks, cameras, videos, folder,
        float(d["start_s"]), ref_clip, length,
        words=words_from_handover(d),
        sound_source=(d.get("audio_files") or {}).get("Full-Mix", ""))
    if not cut:
        return T('That produced no cut -- press Start above again.')
    before_value = d.get("cut") or []
    d["cut"] = [{"start": round(a, 3), "end": round(b, 3), "camera": n}
                    for a, b, n in cut]
    if d["cut"] == before_value:
        print(T('  The cut stays as it was.'))
    else:
        print(T('  The cut has changed: %s shots instead of %s.')
              % (group_text(len(d["cut"])), group_text(len(before_value))))
    d["speakers"] = [{"name": n, "sections": [[round(a, 3), round(b, 3)]
                                                for a, b in segs2]}
                     for n, segs2 in segs]
    d["created_by"] = ('videopodcast-magic %s (cut list refreshed)'
                       % VERSION)
    # Written beside it and moved into place. This file is the whole
    # product of a long run -- the measured offsets, the cut, the speaker
    # statistics -- and writing straight onto it means a failure half way
    # leaves a fragment that the next run silently skips.
    beside = file_path + ".new"
    try:
        with open(beside, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        os.replace(beside, file_path)
    except OSError as e:
        try:
            os.unlink(beside)
        except OSError:
            pass
        print(T('  %s could not be rewritten: %s')
              % (os.path.basename(file_path), e))
    return None


def voices_on_cameras(segment_list, videos, wanted=None, fallback=""):
    """One pseudo track per voice, so write_cut_list can read the cameras.

    The cut asks the tracks which camera a name belongs to. On the
    simple path there is one track and several voices in it, so the
    voices stand in for tracks here -- the same shape, and nothing
    downstream has to know the difference.

    *wanted* is name -> camera, as the interface assigned it; a name it
    does not know, and every name at all where nothing was handed over,
    falls back to *fallback*. All on one camera is not a defect: then
    the cut falls at the change of speaker instead of between cameras.
    """
    wanted = dict(wanted or {})
    after_name = dict((os.path.basename(v), v) for v, _info in videos)
    after_file = ByFile((v, v) for v, _info in videos)
    out = []
    for name, _segs in segment_list or ():
        pick = wanted.get(name) or ""
        camera = after_name.get(pick) or after_file.get(pick) \
            if pick else ""
        out.append({"name": name, "camera": camera or fallback})
    return out


def widest_frame(sizes):
    """Pick the largest frame that a camera really recorded.

    Not the largest width beside the largest height: a landscape and a
    portrait camera in one production would then give a square frame that
    no camera has, and Resolve scales everything into it.
    """
    if not sizes:
        return (None, None)
    return max(sizes, key=lambda wh: (wh[0] * wh[1], wh[0]))








def safe_filename(name):
    return re.sub(r"[^A-Za-z0-9_.+-]", "_", name) or "track"


PHAT_BAND = (300.0, 3500.0)


def gcc_phat_offset(x, y, rate, max_ms=120.0):
    """Return by how many milliseconds y arrives later than x.

    GCC-PHAT: the cross spectrum is normalised to magnitude one across the
    speech band so only the phase counts. Against reverberation and against
    different microphones that is far more robust than a plain cross
    correlation, and it measures to a fraction of a sample rather than to an
    envelope grid. Returns (milliseconds, sharpness of the peak).
    """
    n = 1 << int(np.ceil(np.log2(len(x) + len(y))))
    X, Y = np.fft.rfft(x, n), np.fft.rfft(y, n)
    R = np.conj(X) * Y
    f = np.fft.rfftfreq(n, 1.0 / rate)
    band = (f >= PHAT_BAND[0]) & (f <= PHAT_BAND[1])
    W = np.zeros_like(R)
    W[band] = R[band] / np.maximum(np.abs(R[band]), 1e-12)
    r = np.fft.irfft(W, n)
    size = int(max_ms / 1000.0 * rate)
    corr_window = np.concatenate([r[-size:], r[:size + 1]])
    k = int(np.argmax(corr_window))
    peak = float(corr_window[k])
    if 0 < k < len(corr_window) - 1:
        a, b, c = corr_window[k - 1], corr_window[k], corr_window[k + 1]
        denominator = a - 2 * b + c
        fine = 0.5 * (a - c) / denominator if abs(denominator) > 1e-12 else 0.0
    else:
        fine = 0.0
    return ((k - size + fine) / rate * 1000.0,
            peak / (float(np.std(corr_window)) + 1e-12))


def _block_levels(data, rate, block=1.0):
    """Return the level per second and each track's own speech level.

    A fixed threshold fails because the recorders are set to different
    gains: it would treat the loudest track as always active and the
    quietest as never.
    """
    nb = int(block * rate)
    count = min(len(x) for x in data) // nb
    level = np.array([[float(np.sqrt((x[j * nb:(j + 1) * nb] ** 2).mean()))
                       for j in range(count)] for x in data])
    speech = []
    for row in level:
        present = row[row > 0]
        speech.append(float(np.percentile(present, 90)) if len(present) else 0.0)
    return level, np.array(speech)


def _windows_for_pair(level, speech, i, j, loud=10.0, faint=6.0,
                       at_most=14):
    """Return the blocks in which i speaks and j does not.

    Each track is measured against its *own* speech level, not against the
    others. Otherwise every quietly recorded track would drop out.
    """
    limit_i = max(speech[i] * (10 ** (-loud / 20.0)), 10 ** (-50 / 20.0))
    limit_j = speech[j] * (10 ** (-faint / 20.0))
    good = np.where((level[i] > limit_i) & (level[j] < limit_j))[0]
    if len(good) <= at_most:
        return list(good)
    step = len(good) / float(at_most)
    return [good[int(k * step)] for k in range(at_most)]


# Three points is the least a line through three unknowns can be drawn
# through, and drawn through three it goes exactly -- so three is the
# floor, not a good number.
ENOUGH_WINDOWS = 3
# How far the phase peak has to stand out of the noise around it before
# a second of bleed counts as measured.
SHARP_ENOUGH = 10.0



def measure_offsets_by_crosstalk(tracks, rate=16000):
    """Measure the crosstalk window by window.

    When one person speaks, their voice is faintly in the other microphones
    too -- always a few milliseconds *later*, the time sound takes to travel.
    Returns {(i, j): [(time, milliseconds), ...]} for "i speaks, measured in
    j", plus a list of what failed.
    """
    data = parallel_map(
        tracks,
        lambda track: np.asarray(decode_audio(track["axis"], rate=rate),
                                 dtype=np.float64))
    level, speech = _block_levels(data, rate)
    measurements, lines, nb = {}, [], int(rate)
    for i, track in enumerate(tracks):
        for j in range(len(tracks)):
            if j == i:
                continue
            window = _windows_for_pair(level, speech, i, j)
            # Both failures below carry their number. They are two
            # different recording faults with two different remedies --
            # everybody talking over each other, against bleed too weak
            # or too reverberant to measure -- and without the number
            # nobody can tell them apart from the line.
            if len(window) < ENOUGH_WINDOWS:
                lines.append((track["name"], tracks[j]["name"],
                               T('only %s seconds where %s speaks alone, '
                                 '%s needed')
                               % (group_text(len(window)), track["name"],
                                  group_text(ENOUGH_WINDOWS))))
                continue
            values, best = [], 0.0
            for f in window:
                a = data[i][f * nb:(f + 1) * nb]
                b = data[j][f * nb:(f + 1) * nb]
                ms, sharp = gcc_phat_offset(a, b, rate)
                best = max(best, sharp)
                if sharp >= SHARP_ENOUGH:
                    values.append((f + 0.5, ms))
            if len(values) >= ENOUGH_WINDOWS:
                measurements[(i, j)] = values
            else:
                lines.append((track["name"], tracks[j]["name"],
                               T('bleed too indistinct: %s of %s seconds '
                                 'usable, sharpest %s of %s needed')
                               % (group_text(len(values)),
                                  group_text(len(window)),
                                  decimal_text("%.1f" % best),
                                  decimal_text("%.0f" % SHARP_ENOUGH))))
    return measurements, lines


def solve_pair_offsets(measurements, i, j, highest_clock_drift=100.0):
    """Solve one pair for sound path, offset and clock drift.

    Model: measuring i speaking as heard in j gives sound path + offset(t);
    the reverse gives sound path - offset(t). The sound path is symmetric,
    the offset is not, and if the two clocks run at different speeds it
    grows over time: offset(t) = d0 + k*t.

    Three unknowns, two series of measurements, solved in one least squares
    fit. Returns (path_ms, d0_ms, k_ppm, points, residual_ms) or None if
    one of the two directions is missing. The residual is how far the
    measurements sit from the line the fit drew through them, as a root
    mean square in milliseconds. It says how much the number above is
    worth: three points always fit a line through three unknowns
    exactly, and a residual of zero there means nothing.
    """
    forward, backward = measurements.get((i, j)), measurements.get((j, i))
    if not forward or not backward:
        return None
    lines, values = [], []
    for t, ms in forward:
        lines.append([1.0, 1.0, t])
        values.append(ms)
    for t, ms in backward:
        lines.append([1.0, -1.0, -t])
        values.append(ms)
    A = np.array(lines)
    y = np.array(values)
    with_slope = len(forward) >= 6 and len(backward) >= 6
    if not with_slope:
        A = A[:, :2]
    solution, *_ = np.linalg.lstsq(A, y, rcond=None)
    gone, d0 = float(solution[0]), float(solution[1])
    k = float(solution[2]) * 1000.0 if with_slope else 0.0   # ms/s -> ppm
    if abs(k) > highest_clock_drift:
        # No two clocks drift that fast, so the slope is guesswork. Better to
        # take the fixed offset alone.
        A = A[:, :2]
        solution, *_ = np.linalg.lstsq(A, y, rcond=None)
        gone, d0, k = float(solution[0]), float(solution[1]), 0.0
    left = y - A.dot(solution)
    over = max(1, len(y) - A.shape[1])
    rest = float(np.sqrt(float(np.dot(left, left)) / over))
    return gone, d0, k, len(forward) + len(backward), rest


def verify_alignment(tracks, t0=None, t1=None, limit_ms=1.0,
                      limit_ppm=0.5, drift_allowed=True):
    """Verify the tracks line up, and straighten them if not.

    Measured on the crosstalk, in both directions. The sound path between
    two speakers is symmetric and cancels out; what remains is the fixed
    offset and, with windows spread over the runtime, the clock drift
    between the two recorders. Both are removed by rewriting the track. From
    about 20 ms on, the crossing voice is audible as a second one.
    """
    if len(tracks) < 2:
        return
    print(T('\n  Check against the bleed -- reference is %s:')
          % tracks[0]["name"])
    try:
        measurements, lines = measure_offsets_by_crosstalk(tracks)
    except Exception as e:
        print(T('    not possible: %s') % e)
        return
    for a, b, value in lines:
        print("    %-14s -> %-14s %s" % (a, b, value))

    pairs = {}
    for i in range(len(tracks)):
        for j in range(i + 1, len(tracks)):
            solution = solve_pair_offsets(measurements, i, j)
            if solution is None:
                continue
            pairs[(i, j)] = solution
            gone, d0, k, n, rest = solution
            print(T('    %-14s <-> %-14s sound path %4s ms (%s m), '
                    'offset %6s ms, drift %5s ppm '
                    '(%s points, %s ms left over)%s')
                  % (tracks[i]["name"], tracks[j]["name"],
                     decimal_text("%.1f" % gone),
                     decimal_text("%.2f" % (max(0.0, gone) / 1000.0 * 343.0)),
                     decimal_text("%+.1f" % d0), decimal_text("%+.1f" % k),
                     group_text(n), decimal_text("%.1f" % rest),
                     T('   (sound path negative -- something is wrong)')
                     if gone < -1.0 else ""))
    if not pairs:
        print(T('    No pair measurable -- it stays as it is.'))
        return

    # Position of every track against the first: offset and drift.
    position = {0: (0.0, 0.0)}
    for i in range(1, len(tracks)):
        for j in list(position):
            found = pairs.get((j, i)) or pairs.get((i, j))
            if not found:
                continue
            d0, k = found[1], found[2]
            if (i, j) in pairs:          # measured as (i against j)
                d0, k = -d0, -k
            position[i] = (position[j][0] + d0, position[j][1] + k)
            break
    if t0 is None or t1 is None:
        return

    shifted = []
    for i, track in enumerate(tracks):
        d0, k = position.get(i, (0.0, 0.0))
        if not drift_allowed:
            # --no-drift means the running time stays as recorded. The
            # offset is still corrected; stretching the track is not.
            k = 0.0
        if not track.get("source"):
            continue
        if abs(d0) < limit_ms and abs(k) < limit_ppm:
            continue
        if abs(k) < limit_ppm:
            k = 0.0
        if abs(d0) > 250.0 or abs(k) > 100.0:
            print(T('    %-20s %s ms / %s ppm -- that cannot be '
                    'right, track\n    %-20s stays where it is.')
                  % (track["name"], decimal_text("%+.0f" % d0),
                     decimal_text("%+.0f" % k), ""))
            continue
        # "audio time = a + b * reference time": read d0 too early means
        # shifting a by b*d0, and the drift multiplies b.
        track["a"] = track["a"] + (d0 / 1000.0) * track.get("b", 1.0)
        # The output is compressed by b. A track running too fast -- k
        # negative, the offset shrinking over time -- needs b lowered.
        track["b"] = track.get("b", 1.0) * (1.0 + k * 1e-6)
        track["drift"] = bool(drift_allowed
                           and (track.get("drift")
                                or abs(track["b"] - 1.0) > 1e-7))
        place_track_on_axis(track["source"], track["axis"], track["a"], track["b"], t0, t1,
                       track.get("drift", False))
        shifted.append((track["name"], d0, k))
    if not shifted:
        print(T('    All tracks are in place -- nothing to move.'))
        return
    for name, d0, k in shifted:
        print(T('    %-20s shifted by %s ms%s')
              % (name, decimal_text("%+.1f" % -d0),
                 T(', clock drift %s ppm taken out')
                 % decimal_text("%+.1f" % -k)
                 if abs(k) >= limit_ppm else ""))
    try:
        measurements2, _ = measure_offsets_by_crosstalk(tracks)
    except Exception as e:
        print(T('    Cross-check not possible: %s') % e)
        return
    parts = []
    for i in range(len(tracks)):
        for j in range(i + 1, len(tracks)):
            found = solve_pair_offsets(measurements2, i, j)
            if found:
                parts.append("%s/%s %+.1f ms %+.1f ppm"
                             % (tracks[i]["name"], tracks[j]["name"],
                                found[1], found[2]))
    if not parts:
        print(T('    Cross-check: not measurable'))
        return
    print(T('    Cross-check:'))
    for t in parts:
        print("      %s" % t)


def similarity(a, b):
    """Return how similar two names are, 0 to 1, forgiving of typos."""
    import difflib
    return difflib.SequenceMatcher(None, (a or "").lower(),
                                   (b or "").lower()).ratio()


def without_repeated_words(name):
    """Drop name parts that are already present.

    Compared case insensitively; the order is kept.
    """
    seen, parts = set(), []
    for t in name.split("_"):
        if t and t.lower() in seen:
            continue
        seen.add(t.lower())
        parts.append(t)
    return "_".join(parts)


def counting_digits_off(name):
    """A name without the digits a device counts its files with.

    "Presenter00018" is the eighteenth file of a recorder, "GuestCam001"
    the first of a camera: the numbers say which file, never who. Kept
    where nothing is left without them -- "0008A" is a poor name, but
    it is the only one that file has.
    """
    bare = re.sub(r"[\s_\-.]*\d+[A-Za-z]?$", "", (name or "").strip())
    return bare if len(bare) >= 3 else (name or "").strip()


def camera_for_speaker(speaker, cameras):
    """Return the camera whose name matches this speaker.

    The speaker name is compared with the parts of the camera file name,
    forgiving of typos. A camera carrying two names matches both. Without
    a match there is no suggestion -- a guessed assignment is worse than
    none.
    """
    wanted = (speaker or "").strip().lower()
    if len(wanted) < 3:
        return None
    # A recorder counts its files and so does a camera, and the two
    # counts mean nothing to each other. Measured: "Name00018" against
    # "Names" scored 0.72 and found nothing, the bare name 0.9.
    bare = counting_digits_off(wanted)
    best, best_value = None, 0.0
    for cam in cameras:
        stem = os.path.splitext(os.path.basename(cam))[0]
        for part in [t for t in re.split(r"[_\-. ]", stem) if len(t) >= 3]:
            value = max(similarity(wanted, part),
                        similarity(bare, counting_digits_off(part)))
            # Word starts count too: "Host" is inside "Hosts".
            if part.lower().startswith(wanted) or wanted.startswith(part.lower()):
                value = max(value, 0.9)
            if value > best_value:
                best, best_value = cam, value
    return best if best_value >= 0.8 else None


def guess_camera_name(file_path):
    """Guess a usable track name from a video file name.

    For the case where the camera audio is the track. Pure digit groups
    and the trailing camera identifier drop out, and of the rest the last
    part carries the most meaning. If nothing is left, the whole stem is
    used. The name can be overwritten in the interface.
    """
    stem = os.path.splitext(os.path.basename(file_path))[0]
    parts = [t for t in stem.split("_") if t.strip()]
    left_over = [t for t in parts
              if not re.fullmatch(r"\d+", t)
              and not re.fullmatch(r"[A-Za-z]\d{3,}", t)]
    # Only a fragment left? Then the name was short anyway; better to show the
    # whole stem than one syllable of it.
    return left_over[-1] if len(left_over) >= 2 else stem


def guess_speaker_name(file_path):
    """Guess a usable speaker name from a file name.

    The first name part usually hits; if it is very short the whole stem
    without its trailing number is used. The name can be overwritten in
    the interface.
    """
    stem = os.path.splitext(os.path.basename(file_path))[0]
    m = TRAILING_NUMBER.match(stem)
    without_index_number = m.group(1).rstrip("_-. ") if m else stem
    first_one = re.split(r"[_\-. ]", without_index_number)[0]
    return first_one if len(first_one) >= 3 else without_index_number


# The standard folders of a home directory. On macOS and Windows they
# carry these English names on disk whatever language the system is set
# to -- the translated name is shown, not stored. Linux really does
# rename them and writes the chosen names into user-dirs.dirs, so those
# are read from there rather than guessed from a list of languages.
GENERAL_FOLDERS = ("desktop", "downloads", "documents", "movies", "music",
                   "pictures", "videos", "public", "temp", "tmp")
_general_extra = []


def general_folder_names():
    """Folder names that say nothing about which production this is."""
    if not _general_extra:
        _general_extra.append(set(GENERAL_FOLDERS))
        config = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser(
            os.path.join("~", ".config"))
        try:
            with open(os.path.join(config, "user-dirs.dirs"),
                      encoding="utf-8", errors="replace") as f:
                for line in f:
                    if not line.startswith("XDG_") or "=" not in line:
                        continue
                    where = line.split("=", 1)[1].strip().strip('"')
                    name = os.path.basename(where.rstrip("/"))
                    if name and name != "$HOME":
                        _general_extra[0].add(name.lower())
        except Exception:
            pass
    return _general_extra[0]


def guess_production_name(file_path):
    """Return the production name from the folder holding the files.

    Files sitting directly on a volume or in the home folder have a
    meaningless folder name; then date and time are used instead.
    """
    folder = os.path.dirname(os.path.abspath(file_path))
    name = os.path.basename(folder)
    parent = os.path.dirname(folder)
    general = general_folder_names()
    meaningless = (not name
                    or folder == os.sep                  # root
                    or parent == "/Volumes"              # volume root
                    or folder == os.path.expanduser("~")  # home folder
                    or name.lower() in general)
    if meaningless:
        return 'Production ' + time.strftime("%Y-%m-%d %H-%M")
    return name


# How much shorter than the rest a file has to be before one with no
# place is taken for a jingle. A jingle is orders below the material it
# sits among; a recording that belongs to the shoot and merely fits
# nothing is about as long as the rest, and a tenth lies between them.
INTRO_SHORT_ENOUGH = 0.1


def files_far_shorter(some, length_of):
    """Which of *some* are far shorter than the material around them.

    Held against the middle of the others rather than against a length
    written down: what counts as short is what the rest of the shoot
    is, and that differs from one production to the next. Shortest
    first.
    """
    out = []
    for p in some:
        others = sorted(s for q, s in length_of.items() if q != p)
        if p not in length_of or not others:
            continue
        middle = others[len(others) // 2]
        if middle > 0 and length_of[p] <= middle * INTRO_SHORT_ENOUGH:
            out.append(p)
    return sorted(out, key=lambda p: length_of[p])


def axis_text(data):
    """The line under the axis: how it was found, and what did not fit.

    Read off the finished answer rather than put together beside it, so
    the count and the list it counts cannot drift apart.
    """
    text = (T('time axis measured and tied to the timecode')
            if (data or {}).get("absolute")
            else T('time axis measured -- jumps land at the same point'))
    weak = (data or {}).get("weak") or ()
    if weak:
        text += TN(len(weak), ', %s file does not fit',
                   ', %s files do not fit') % group_text(len(weak))
    return text


def measure_time_axis(paths, tc_of=lambda p: None, HOP=5.0):
    """Determine how all files sit relative to each other.

    The longest recording is the reference: it overlaps most with the
    others. Measured with the same method as the run itself, so the preview
    cannot show a different axis from the one the run computes.

    *tc_of* returns the timecode of a file or None. If any file carries one,
    the whole axis hangs off it and the others get a real wall clock time
    instead of an invented one.

    Returns (result, text). The result is {} or {"axis", "clock",
    "absolute", "weak", "unplaceable", "brief", "no_place"}; "clock" is
    how fast each recorder ran, the b the run takes out. Both are keyed
    by path_key, as axis_still_valid keys what it reads out of the
    project file; the four lists keep the names they came in with.

    Four lists, narrowing. "weak" is a file that fits badly. "no_place"
    are the weak ones no timecode places either -- those sit nowhere,
    and that is what bars the wide shot. "unplaceable" is narrower
    still: under the floor as well, which is what a file has to be
    before it is proposed for leaving out. "brief" are the ones with
    no place that are far shorter than the material around them.
    """
    # Every file at once: each envelope is read and computed on its
    # own, and over hours of 4K this is the longest part of the
    # measurement.
    def curve_of(file_path):
        try:
            return video_envelope(file_path, HOP, 4000)
        except Exception:
            return None

    envelopes = {}
    for p, env in zip(paths, parallel_map(paths, curve_of)):
        if env is not None and len(env) > 200:
            envelopes[p] = env
    if len(envelopes) < 2:
        return ({}, "" if envelopes else T('time axis not measurable'))
    reference = max(envelopes, key=lambda p: len(envelopes[p]))
    axis, weak, lost = {reference: 0.0}, [], []
    # Not "clocks": that one holds timecodes a few lines down.
    clock_speed = {reference: 1.0}
    others = [p for p in envelopes if p != reference]
    clocks = dict((p, tc_of(p)) for p in paths)

    def against_reference(file_path):
        try:
            # The same method as the run: sample points over the whole
            # runtime, a regression line, the median.
            a_s, b, st = align_envelopes(envelopes[reference],
                                          envelopes[file_path], HOP,
                                          warn=os.path.basename(file_path))
            return a_s, b, st.get("quality", 0.0)
        except Exception:
            return None

    for p, answer in zip(others, parallel_map(others, against_reference)):
        if answer is None:
            continue
        a_s, b, g = answer
        if abs(g) < SOUND_MATCH_ENOUGH:
            # No phase way here, and that is measured rather than
            # forgotten: laid in at this floor it placed all ten files
            # of the interview folder nineteen hours out, where the
            # window had placed none and said so. See align_audio_to_video.
            weak.append(p)
            if cannot_be_placed({"unplaceable": g < WEAK_MATCH}, clocks.get(p),
                                [t for q, t in clocks.items() if q != p]):
                lost.append(p)
            continue
        # Divided by b, exactly as the run divides it before it writes
        # the track: a is where the recording sits in its own time, and
        # its own time runs at b.
        axis[p] = -a_s / b
        clock_speed[p] = b
    # Held against a camera as well: against a sound recording a jingle
    # and a camera read too close together to tell apart
    # (measurements.md, 31.8.2026). The run used this floor all along.
    cameras = [p for p in envelopes if p.lower().endswith(VIDEO_SUFFIXES)]
    if len(cameras) > 1:
        camera_ref = max(cameras, key=lambda p: len(envelopes[p]))
        for p in cameras:
            if p == camera_ref or p in weak:
                continue
            try:
                _a, _b, st = align_envelopes(envelopes[camera_ref],
                                             envelopes[p], HOP,
                                             warn=os.path.basename(p))
            except Exception:
                continue
            if (st.get("quality", 0.0) < CAMERA_MATCH_ENOUGH
                    and not fit_places_it(st)):
                # The same second way the run leaves open at this floor:
                # where a clock places the file, the sound is not asked.
                # It is still marked, so the list says the sound was not
                # recognised -- but it keeps the place it was given.
                st["unplaceable"] = True
                weak.append(p)
                if cannot_be_placed(st, clocks.get(p),
                                    [t for q, t in clocks.items()
                                     if q != p]):
                    axis.pop(p, None)
                    clock_speed.pop(p, None)
    # A file that fits nothing and is far shorter than everything around
    # it is a jingle rather than a camera. A clock that places it beats
    # the sound here as everywhere. The lengths are here anyway: an
    # envelope holds one value every HOP milliseconds.
    nowhere = files_with_no_place(weak, clocks)
    brief = files_far_shorter(
        nowhere, dict((p, len(e) * HOP / 1000.0)
                      for p, e in envelopes.items()))
    if len(axis) < 2:
        # No axis, but the measurement did happen and knows which files
        # it could not place. Thrown away here, the one file that fits
        # nothing would come out of a two-file production unmarked.
        return ({"axis": {}, "clock": {}, "absolute": False, "weak": weak,
                 "unplaceable": lost, "brief": brief,
                 "no_place": nowhere},
                T('time axis not measurable'))
    origin = min(axis.values())
    for p in axis:
        axis[p] -= origin
    # The median offset is used so one outlier cannot skew everything.
    offsets = sorted(t - axis[p] for p in axis
                       for t in [tc_of(p)] if t is not None)
    absolute = bool(offsets)
    if absolute:
        middle = offsets[len(offsets) // 2]
        for p in axis:
            axis[p] += middle
    # Not before here: everything above reads the file itself, and the
    # timecode is asked for under the name that was passed in.
    axis = dict((path_key(p), t) for p, t in axis.items())
    speed = dict((path_key(p), b) for p, b in clock_speed.items()
                 if path_key(p) in axis)
    answer = {"axis": axis, "clock": speed, "absolute": absolute,
              "weak": weak, "unplaceable": lost, "brief": brief,
              "no_place": nowhere}
    return answer, axis_text(answer)


def envelope_seconds(path, HOP=5.0):
    """How long a file runs, out of the envelope already measured.

    No second reading of the file: the curve is in memory or in the
    cache by the time the axis is worked out, and it holds one value
    every HOP milliseconds. 0.0 where there is none.
    """
    try:
        return len(video_envelope(path, HOP, 4000)) * HOP / 1000.0
    except Exception:
        return 0.0


def block_at(blocks, when, begins):
    """Which block of a recording holds a moment, and how far into it.

    A recording written in pieces is one recording, and every piece has
    a place of its own -- so the piece holding a moment is the last one
    that starts before it. *begins* answers where a piece starts, which
    lets the same walk serve the measured axis and the files' own
    clocks. Returns (path, seconds into it), or (None, None).
    """
    before = [(begins(p), p) for p in blocks or ()]
    before = [(t, p) for t, p in before if t is not None and t <= when]
    if not before:
        # Nothing of this recording had started yet. Playing its front
        # here would sound it against a picture it does not belong to,
        # which is the very mistake the axis exists to prevent.
        return None, None
    t, p = max(before)
    return p, when - t


def blocks_after_their_head(data, blocks, length_of=envelope_seconds):
    """Put a continuation behind its head block.

    A recording is one recording, and the grouping settles where its
    parts lie: the head's place plus what runs before. *blocks* is
    {head: [head, second, ...]} and is the whole of the distinction --
    a block taken out and put back in on its own is not in there, so it
    is a recording of its own, measured and free to fail.
    """
    axis = (data or {}).get("axis") or {}
    speed = (data or {}).get("clock") or {}
    put = {}
    for row in (blocks or {}).values():
        keys = [path_key(p) for p in row or ()]
        if len(keys) < 2 or keys[0] not in axis:
            continue
        at = axis[keys[0]]
        for before, key in zip(row, keys[1:]):
            runs = float(length_of(before) or 0.0)
            if runs <= 0.0:
                # Without the length of the block in front there is no
                # place to work out. Guessing one would put the rest of
                # the recording somewhere and call it measured.
                break
            at += runs
            put[key] = (at, speed.get(keys[0], 1.0))
    if not put:
        return data
    axis.update((k, v[0]) for k, v in put.items())
    speed.update((k, v[1]) for k, v in put.items())
    data["axis"], data["clock"] = axis, speed
    return data


def axis_with_blocks(paths, tc_of=lambda p: None, HOP=5.0, blocks=None,
                     length_of=envelope_seconds):
    """Measure a recording made of blocks as one recording.

    The head is measured like any other file, the continuations are not
    measured at all: they are taken to fit, and their place follows
    from the head. So a tail of a few minutes can no longer turn down
    an hour of material -- and whoever wants one weighed on its own
    takes it out of the recording and puts it back in as a file, which
    makes it a recording of its own and measured like any other.
    """
    tails = set(path_key(p) for row in (blocks or {}).values()
                for p in (row or ())[1:])
    data, text = measure_time_axis(
        [p for p in paths if path_key(p) not in tails], tc_of, HOP)
    return blocks_after_their_head(data, blocks, length_of), text


def file_fingerprint(file_path):
    """Return what identifies a file again: path, mtime, size.

    No hash: over hours of material that would take longer than what it
    secures. Replacing a file practically always changes at least one of the
    two.
    """
    try:
        st = os.stat(file_path)
        return [os.path.abspath(file_path), int(st.st_mtime), st.st_size]
    except OSError:
        return None


# How much is read at a time when marking a file by its content. A
# larger block buys nothing: the hashing sets the pace, not the disk.
CONTENT_BLOCK = 1 << 20


def file_content_mark(file_path):
    """Return what a file holds, as one string over size and content.

    For a file whose name says nothing: a mix is written into a fresh
    folder on every run, so path and time can never meet themselves,
    and a modification time cannot tell two writes inside one second
    apart either. Costs about a third of a second per gigabyte, read
    or cached. "" where the file cannot be read.
    """
    mark = hashlib.sha1()
    try:
        with open(file_path, "rb") as f:
            mark.update(b"%d\n" % os.fstat(f.fileno()).st_size)
            for block in iter(lambda: f.read(CONTENT_BLOCK), b""):
                mark.update(block)
    except OSError:
        return ""
    return mark.hexdigest()


def timeline_entries(axis, clocks):
    """The measured place of every file, as the project file keeps it.

    The clock speed rides along with the position: measuring it again
    costs the same minutes, and a file that changed is caught by its
    size and time anyway.
    """
    out = []
    for p, start in (axis or {}).items():
        k = file_fingerprint(p)
        if k:
            out.append({"path": k[0], "mtime": k[1], "size": k[2],
                        "start_s": round(start, 3),
                        "clock": round(float(
                            (clocks or {}).get(path_key(p), 1.0)), 9)})
    return out


def axis_still_valid(d, paths, fingerprint=file_fingerprint):
    """Report whether a previously measured axis still applies to these files.

    All or nothing: one changed file moves the others with it, since the
    axis is a statement about their relationship. A half valid axis would be
    worse than none, because it would look right.

    Returns {"axis", "clock", "weak", "absolute"} or None, keyed by
    path_key; without a stored clock speed a file comes back at 1.0."""
    known = {}
    for e in ((d or {}).get("timeline") or []):
        stored = e.get("path")
        if stored:
            known[path_key(stored)] = e
    axis, speed = {}, {}
    for file_path in paths:
        k = fingerprint(file_path)
        e = known.get(path_key(k[0])) if k else None
        if not e or e.get("mtime") != k[1] or e.get("size") != k[2]:
            return None
        axis[path_key(k[0])] = float(e.get("start_s") or 0.0)
        speed[path_key(k[0])] = float(e.get("clock") or 1.0)
    if not axis:
        return None
    return {"axis": axis, "clock": speed, "weak": [],
            "absolute": bool((d or {}).get("timeline_absolute"))}


def axis_worth_measuring(files, every, state, fingerprint=file_fingerprint):
    """Whether the time axis still has something new to say.

    The tables ask again on every rebuild, the answer moves the Kind of
    a file with no place, and that rebuilds the tables. Material that
    has not changed and files an answer has reached leave nothing to
    measure. The list handed in is no mark: a file whose Kind is not a
    camera drops out of it. The question is noted on *state*, except
    while one is running -- that answer is about the older list.
    """
    mark = frozenset(tuple(fingerprint(p) or (p, 0, 0)) for p, _a in files)
    want = set(path_key(p) for p in every)
    if (state.get("axis_answered") == mark
            and want <= (state.get("axis_covered") or set())):
        return False
    if not state.get("axis_running"):
        state["axis_asked"], state["axis_asking"] = mark, want
    return True


def axis_answer_kept(state):
    """Note what the answer just given was about.

    Material that changed meanwhile starts the list of files reached
    afresh; otherwise two questions over one unchanged set add up.
    """
    if state.get("axis_answered") != state.get("axis_asked"):
        state["axis_covered"] = set()
    state["axis_answered"] = state.get("axis_asked")
    state["axis_covered"] = ((state.get("axis_covered") or set())
                             | (state.get("axis_asking") or set()))


def recordings_text(chains, file_count):
    """Return the header line of the audio group.

    Several blocks of one recording are one recording, not several. While
    both counts agree the file count is enough; otherwise the line would
    draw a distinction that does not exist.
    """
    if chains == file_count:
        return TN(file_count, '%s file', '%s files') % group_text(file_count)
    return TN(chains, '%s recording from %s files',
              '%s recordings from %s files') % (group_text(chains),
                                                group_text(file_count))


def pending_prework(paths, having_audio=(), has_audio=lambda p: False,
                    has_env_curve=lambda p: False,
                    has_channels=lambda p: False,
                    has_tracks=lambda p: True):
    """Return the prework still to be done: envelopes for all, audio for some.

    Reading the same file twice costs minutes over hours of material, so it
    is asked rather than queued blindly. The two are separate: the envelope
    may already be there while the audio is missing.

    *has_audio* may return None: the file cannot even be queried, and it
    stays out entirely, envelope included. Queueing it here would report the
    same error four times instead of once during the run.

    A file with more than one channel is measured as well: whether its
    channels are one pair of microphones or several tracks decides what
    the later tabs are even offered, and reading every channel of an
    hour of audio is not something to do in the window thread.

    Returns a list of (absolute path, task) in working order, where the
    task is "audio", "envelope" or "channels".
    """
    wants_audio = set(os.path.abspath(p) for p in having_audio)
    out = []
    for file_path in paths:
        a = os.path.abspath(file_path)
        if not os.path.exists(a):
            continue
        if a in wants_audio:
            present = has_audio(a)
            if present is None:
                continue
            if not present:
                out.append((a, "audio"))
        if not has_env_curve(a):
            out.append((a, "envelope"))
        try:
            wide = channel_count(a) > 1
        except Exception as e:
            # Swallowing this leaves the file list saying "being looked
            # at" for ever, with nothing in the work list and therefore
            # no bar either -- the one state that looks exactly like a
            # crash. So it is said instead.
            print(as_warn(T('  %s: how many channels it has cannot be '
                            'determined (%s) -- it is not measured')
                          % (os.path.basename(a), str(e).strip()[:60])))
            wide = False
        if wide:
            if not has_channels(a):
                out.append((a, "channels"))
            elif not has_tracks(a):
                # Only once the channels are known: what has to be cut
                # out follows from that measurement.
                out.append((a, "split"))
    return out


def every_audio_block(files, blocks_of, using_audio=()):
    """Every file a run would listen to, blocks included.

    *files* is the selection as (path, kind) pairs, *blocks_of* what the
    search found for each recording. The selection holds what somebody
    picked; a recording made of blocks was found in the folder, and its
    continuations are not in the list. They still have to be measured
    and cut, or the tracks of a multi-part recording would come from the
    first block only.

    *using_audio* are the video files whose sound was set to "use". They
    belong in the same list and not in a second one beside it: this list
    used to hold audio files alone, which is why the channel splitting
    never started for a camera carrying two clip-on microphones.
    """
    out = [os.path.abspath(p) for p, a in files if a == "audio"]
    for p in using_audio:
        if os.path.abspath(p) not in out:
            out.append(os.path.abspath(p))
    for row in blocks_of.values():
        for x in row:
            if x not in out:
                out.append(x)
    return out


def window_suggestion(entries, fps=30.0):
    """Suggest the In point and the Out point from what the cameras offer.

    As far as the cameras reach -- from the earliest start to the latest
    end. That is what happens without an entry anyway; here it is visible
    and can be adjusted.

      *entries*  [(start on the clock or None, duration)]

    Returns (in_point, out_point, absolute). If no file carries a start time
    the suggestion is relative: from zero to the length of the longest. Without
    any usable entry ("", "", False).
    """
    starts = [(t, d) for t, d in entries if t is not None]
    if starts:
        return (timecode_string(min(t for t, _d in starts), fps),
                timecode_string(max(t + (d or 0.0) for t, d in starts), fps),
                True)
    lengths = [d for _t, d in entries if d]
    if not lengths or max(lengths) <= 0:
        return "", "", False
    # Whole seconds are enough here, and the mark depends on the
    # language, so it is asked for explicitly.
    return "+0:00", "+%s" % as_hms(max(lengths), ".").split(".")[0], False


def has_sound(file_path):
    """Whether this file carries an audio stream at all.

    Asked of a camera before its audio is made into a track by itself:
    a camera nobody plugged a microphone into is no answer to the
    question where the sound comes from.
    """
    try:
        return any(s.get("codec_type") == "audio"
                   for s in ffprobe_json(file_path).get("streams") or [])
    except Exception:
        return False


def cameras_with_own_audio(videos, audio_files, ticked=(), sound_of=None):
    """Which cameras contribute their audio as a track, and which by rule.

    A field set by hand decides, and nothing else -- with one exception,
    the case where there is nothing to decide: a single video file that
    carries sound, and not one audio recording beside it. Then that
    sound is the only sound there is, and a run without it would have
    nothing at all to work on. Two cameras are a choice again, and a
    choice belongs to the person, not to the program.

    Derived, never stored. As soon as an audio recording joins the
    selection the exception no longer holds and the tick is gone by
    itself, so no forgotten automatic tick is left behind.

    *sound_of* answers whether a video carries audio; without it every
    video counts as carrying some.

    Returns (cameras, forced), *forced* being the ones nobody ticked.
    """
    wanted = {os.path.abspath(b) for b in (ticked or ())}
    by_hand = [b for b in videos if os.path.abspath(b) in wanted]
    if by_hand or audio_files or len(videos) != 1:
        return by_hand, []
    if sound_of is not None and not sound_of(videos[0]):
        return [], []
    return list(videos), list(videos)


def assignment_rows(audio_files, videos, own_flag_cameras=(),
                    split_of=None, apart=(), together=()):
    """Return the rows for the upper table.

    The normal case: one row per audio recording (or per chain of blocks
    belonging together), plus the cameras contributing their audio as a
    track -- those are input tracks like any other and belong in the same
    table.

    "Like any other" includes the channels. A camera whose two channels
    carry two clip-on microphones -- a DJI Osmo does that -- gives two
    rows, judged and cut by exactly the same rule as a recorder file. The
    field on the camera says nothing more than "do not throw this audio
    away"; what it becomes is decided by the same measurement.

    There is no special case any more. Until 25.8.2026 two or more
    cameras and no audio recording made every camera a track by itself.
    Nothing can tell a radio microphone in the video track from a room
    microphone, so it is asked per file: *own_flag_cameras* is the whole
    answer.

    Returns (chains, camera_audio, own_audio_tracks). *camera_audio* is
    the retired special case and now always False. The last one is
    {track: the camera it came out of}, empty where none contributes.
    """
    chains = (list(group_recording_parts(audio_files, apart=apart,
                                         together=together))
              if audio_files else [])
    if split_of:
        chains = expand_chains_to_tracks(chains, split_of)
    rows, own = [], ByFile()
    for b in list(own_flag_cameras or ()):
        pieces = [x for x in (split_of(b) or ())] if split_of else []
        for piece in (pieces or [b]):
            rows.append(([piece], []))
            own[piece] = os.path.abspath(b)
    return chains + rows, False, own


def preselected_camera(old, targets, speaker, videos, own_camera=""):
    """Return the camera an audio track is preselected to.

    A manual setting still applies, but only while that camera still exists.
    Otherwise the speaker name is searched for. Without a match it stays on
    the mix: a wrongly guessed camera looks like a decision and is then
    never checked again.

    *own_camera* is where audio out of a camera starts: that camera. It is
    a preselection, not a rule -- a clip-on microphone plugged into one
    camera may well belong to a person another camera is filming -- so a
    setting made by hand comes first.
    """
    if old and old in targets:
        return old
    if own_camera:
        return own_camera
    hit = camera_for_speaker(speaker, videos)
    return os.path.basename(hit) if hit else MIX_ONLY


def camera_to_remember(camera, derived, keep=None):
    """What of an audio row's camera is written into the project.

    Only a real override. One the program worked out itself goes back
    as nothing, so the next rebuild works it out again -- stored, a
    name changed afterwards no longer moves the camera. *keep* is what
    a quiet row falls back on: there the mix is the absence of a
    choice, not one.
    """
    if camera == MIX_ONLY and keep:
        return keep
    return None if camera == derived else camera


def camera_row_cameras(old, targets, speaker, videos, own_camera=""):
    """The camera a row shows, and the one the program would give alone.

    Two answers to one question: the second is asked with nothing
    remembered, and only a camera that differs from it is written down.
    """
    return (preselected_camera(old, targets, speaker, videos, own_camera),
            preselected_camera(None, targets, speaker, videos, own_camera))


def camera_shortfall_lines(who, rows, voices):
    """What to say about speakers who get no shot of their own.

    Nothing where there are none. Where it is everybody, a second line:
    no camera then carries a speaker, every shot is the same one, and
    the cut says nothing -- worth knowing before the hours of computing
    rather than out of the log afterwards.
    """
    if not who:
        return []
    out = [T('No camera of their own: %s') % ", ".join(who)]
    if len(who) >= len(rows) + len(voices):
        out.append(T('   -- that is everybody, so every shot goes to the '
                     'same camera.'))
    return out


def without_own_camera(rows, voices, multitrack_on, voiced=()):
    """Who goes into the mix but gets no shot of their own.

    Read off the assignment as it stands, for the sentence shown when
    Start is pressed. It is information and not a complaint: whoever
    set somebody to "no camera of its own" wanted it that way. What
    they could not see until now is the list of them all in one place,
    before three hours of computing rather than after.

    Two kinds of row are passed over, because neither is anybody being
    left out of the picture: a recording whose separated voices stand
    under it does not answer for itself -- the voices carry the
    cameras -- and without multitrack every recording goes into every
    camera anyway. A name nobody typed is passed over as well; an
    empty entry in the list would say nothing.

    *rows* are (blocks, name, camera), *voices* are (name, camera).
    """
    voiced = set(voiced or ())
    pairs = [(name, camera) for blocks, name, camera in rows
             if multitrack_on and os.path.abspath(blocks[0]) not in voiced]
    out = []
    for name, camera in pairs + list(voices):
        name = (name or "").strip()
        if camera == MIX_ONLY and name and name not in out:
            out.append(name)
    return out


def name_already_in(stem, speaker):
    """Whether the speakers' names already stand in the camera's name.

    "Guest" in "GuestCam001" -- saying it again puts one word twice
    into a name that travels into Resolve. Every one of them has to be
    there, not just one: a camera called "Hosts" carrying "Host" and
    "Co-host" says nothing about the second.
    """
    low = (stem or "").lower()
    names = [x.strip().lower() for x in speaker or () if (x or "").strip()]
    return bool(names) and all(n and n in low for n in names)


def camera_output_name(production, camera, speaker=()):
    """Build the name of the new video file.

    The speakers sit in the middle of the camera name, behind its first
    part. The front stays readable as which camera it was, and the camera
    identifier stays at the back.

    Where the camera is already named almost like the speaker, the name
    would otherwise appear twice. The comparison is forgiving, so a typo
    counts as the same.
    """
    stem = os.path.splitext(os.path.basename(camera))[0]
    # Split only where what follows carries a number: that is a
    # counter, and the speaker belongs in front of it. A camera named
    # after a person carries none -- "First Last" came back as
    # "First_<speaker>_Last".
    parts = re.split(r"[_\-. ]", stem, maxsplit=1)
    if len(parts) == 2 and not re.search(r"\d", parts[1]):
        parts = [stem]
    who = "+".join(x.strip() for x in speaker if (x or "").strip())
    if parts and who and (similarity(parts[0], who) >= 0.85
                          or name_already_in(stem, speaker)):
        who = ""
    front = (production or "").strip() or 'Production'
    # A stem that already begins with the production is not split any
    # further: doing so put the speaker inside the production's own
    # name. It happens on a second run over an output folder.
    if front and stem.lower().startswith(front.lower()):
        parts = [stem]
    if len(parts) == 2 and not who:
        name = "%s_%s" % (front, stem)
    elif len(parts) == 2:
        name = "%s_%s_%s_%s" % (front, parts[0], who, parts[1])
    else:
        name = "_".join(x for x in (front, stem, who) if x)
    return without_repeated_words(name)


def together_chains(together):
    """Bring the by-hand groupings into one ordered list per recording.

    Given as [[a, b], [b, c]] they mean one recording a, b, c: naming a
    file in two groups joins those groups. Order is kept -- the first
    time a file is named is where it sits.
    """
    rows = []
    for group in (together or ()):
        wanted = [os.path.abspath(x) for x in group if x]
        if len(wanted) < 2:
            continue
        hit = [r for r in rows if any(x in r for x in wanted)]
        if not hit:
            rows.append(list(dict.fromkeys(wanted)))
            continue
        first = hit[0]
        for other in hit[1:]:
            first += [x for x in other if x not in first]
            rows.remove(other)
        first += [x for x in wanted if x not in first]
    return rows


def group_recording_parts(paths, no_followups=False, apart=(), together=()):
    """Group the selected audio files into recordings.

    Numbered continuations are searched from the first block, and only
    seamless ones are appended. Selecting just the first block or all of
    them comes to the same thing.

    *apart* names blocks that must stand on their own. A block taken out
    of a recording by hand would otherwise be found again on the very
    next rebuild -- the search looks in the folder, not in the
    selection. Put back later it is a file in its own right; only
    removing the whole recording and adding it again joins it up again.

    *together* is the other direction: files that belong to one recording
    although nothing in their names says so. Each named file brings the
    blocks that already belong to it, so naming the first block of a
    three block recording adds all three. Both are by hand and both beat
    the measurement, so a file named in *apart* stays out even of a group
    it was put into.
    """
    apart = FileSet(apart or ())

    def with_its_blocks(row):
        """Each named file plus the blocks already found for it.

        Only what fits: the channel count and the sample rate have to
        match the first block. Everything after the join treats the
        blocks as one recording, and a channel that is number three in
        one block and number four in the next would make nonsense of
        that.
        """
        out, refused = [], []
        for x in row:
            if not os.path.exists(x):
                refused.append((os.path.basename(x), T('not found')))
                continue
            found = [x]
            if not no_followups and x not in apart:
                try:
                    found, _ = find_continuation_files(x)
                except Exception:
                    found = [x]
            for y in found:
                y = os.path.abspath(y)
                if y in apart or y in out:
                    continue
                if out:
                    fits, why = shapes_match(out[0], y)
                    if not fits:
                        refused.append((os.path.basename(y), why))
                        continue
                out.append(y)
        return out, refused

    made = [with_its_blocks(row) for row in together_chains(together)]
    # Two groups can end up holding the same block: each named file
    # brings the blocks already found for it, and two different blocks of
    # one numbered chain bring the whole chain. A block belongs to one
    # recording, so the first group to claim it keeps it.
    by_hand, turned_away, claimed = [], {}, set()
    homeless = {}
    for row, refused in made:
        mine = [x for x in row if x not in claimed]
        notes = list(refused) + [
            (os.path.basename(x), T('already in another recording'))
            for x in row if x not in mine]
        if len(mine) < 2:
            # Nothing left to group. The notes still have to reach
            # somebody, or a file named by hand and turned away would
            # vanish without a word; they go to the recording the one
            # remaining file ends up in.
            for x in mine or row:
                homeless.setdefault(x, []).extend(notes)
            continue
        claimed.update(mine)
        turned_away[len(by_hand)] = notes
        by_hand.append(mine)
    put = {}
    for i, row in enumerate(by_hand):
        for x in row:
            put[x] = i
    pending = sorted(paths, key=lambda x: os.path.basename(x).lower())
    chains, taken, done_by_hand = [], set(), set()
    for p in pending:
        a = os.path.abspath(p)
        if a in taken:
            continue
        if a in put:
            # A grouping made by hand: exactly these files, in the order
            # they were named, and nothing searched in the folder.
            i = put[a]
            if i in done_by_hand:
                continue
            done_by_hand.add(i)
            row, discarded = list(by_hand[i]), list(turned_away.get(i) or [])
            for path in row:
                taken.add(path)
                discarded = discarded + homeless.pop(path, [])
            chains.append((row, discarded))
            continue
        if no_followups or a in apart:
            row, discarded = [a], []
        else:
            try:
                row, discarded = find_continuation_files(a)
            except Exception:
                row, discarded = [a], []
            row = [x for x in row if os.path.abspath(x) not in apart
                   and os.path.abspath(x) not in put]
        for path in row:
            taken.add(os.path.abspath(path))
            discarded = discarded + homeless.pop(path, [])
        chains.append((row, discarded))
    # A note whose file never reached a recording of its own -- it was
    # claimed by another group, or it is not in the list at all. It still
    # has to be read somewhere, so it goes to the first recording rather
    # than nowhere.
    if homeless and chains:
        left = [note for notes in homeless.values() for note in notes]
        chains[0] = (chains[0][0], list(chains[0][1]) + left)
    return chains


def recording_family(file_path):
    """Every block that would belong to this recording, marks aside.

    Used when a whole recording leaves the list: the marks of its blocks
    go with it, so adding the files again joins them up as before.
    """
    try:
        row, _discarded = find_continuation_files(os.path.abspath(file_path))
    except Exception:
        row = [os.path.abspath(file_path)]
    return {os.path.abspath(x) for x in row} | {os.path.abspath(file_path)}


def cameras_as_tracks(args):
    """How many cameras contribute their own audio as a track.

    Not a property of the command line but of the material: Camera
    audio is set to "use the audio" at the file, and the answer travels
    in the assignment file. Without one nothing is set and the answer
    is none.
    """
    path = getattr(args, "assign", None)
    if not path or not os.path.exists(path):
        return 0
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (ValueError, OSError):
        return 0
    rows = (d.get("tracks_of") if isinstance(d, dict) else d) or []
    return sum(1 for e in rows if isinstance(e, dict)
               and (e.get("camera_audio") or e.get("own_audio")
                    or e.get("from_camera")))


def check_mode_fits_input(audio_paths, args):
    """Report whether the selection fits the mode. Returns a message or None.

    Recordings are counted, not files: three blocks from one recorder are
    one audio source, not three. A camera counts as a recording once the
    assignment marks its audio as a track -- one microphone recording and
    two cameras with their own sound are three tracks, and Multitrack is
    the right mode for them.

    Several cameras are allowed but not required -- one camera with three
    microphones in front of it is the normal case.
    """
    if not args.multitrack:
        return None
    chains = len(group_recording_parts(audio_paths, args.no_follow_ups,
                                       getattr(args, "apart", ()),
                                       getattr(args, "together", ())))
    chains += cameras_as_tracks(args)
    if chains < 2:
        return as_warn(
            T('MULTITRACK NOT POSSIBLE\n  At least two input tracks are '
              'needed, and only %s was found.\n  A track is a recording of '
              'its own, a channel of a multichannel\n  recorder, or the '
              'audio of a camera -- that counts as soon as its\n  Camera '
              'audio says "use the audio". Without two of them there\n  '
              'is nothing to decouple, and the same file runs through as an\n'
              '  ordinary production.')
            % group_text(chains))
    # A key is only needed where something is going to be sent. With
    # --auphonic-done the tracks are already finished and lie in a
    # folder -- from auphonic.com, or from a mixing desk, or from
    # anywhere else. Asking for a key there refused a run that wanted
    # nothing from auphonic.com, and the only way past it was the key
    # on the command line, which the first rule of this project
    # forbids. Found on 23.8.2026 while comparing with AudioRecorder.
    brings_own = bool(getattr(args, "auphonic_done", None))
    if (not args.auphonic_key
            and not getattr(args, "without_auphonic", False)
            and not brings_own):
        return as_warn(T('MULTITRACK NOT POSSIBLE\n  Without an API key '
                         'there is nothing to send to auphonic.com.\n  With '
                         '--without-auphonic it runs locally instead: '
                         'aligned,\n  mixed and cut, but without de-bleed '
                         'and leveler.'))
    return None


def named_people(pairs):
    """The people in these (name, camera) pairs who have both.

    A name without a camera is somebody in the mix, not somebody on
    screen, and the same name twice is one person.
    """
    return set((n or "").strip() for n, c in pairs
               if (n or "").strip()
               and c not in (IGNORE_AUDIO, MIX_ONLY))


def cut_has_people(pairs, cameras=0):
    """Whether these (name, camera) pairs give a camera cut.

    Two people with a name and a camera, and Multitrack is not part of
    it: the cut reads who speaks when out of one list, and it makes no
    difference to that list whether the people were told apart by
    having a microphone each or by the separation taking one recording
    apart. Hanging the cut off the tick hid it from everybody with one
    recording and four voices in it.

    The cameras may be the same one. Then nothing is switched, but the
    cut still falls at every change of speaker, and Resolve gets one
    clip per person instead of one long take -- write_cut_list says so
    itself where it finds a single camera.

    One person is a cut too, which is what *cameras* is for: with a
    second camera nobody is on, the picture is theirs and the wide shot
    breaks it up every "Wide shot after" seconds. Measured on
    25.8.2026: one speaker over five minutes on two cameras gives 15
    shots, 7 of them the wide one. With only their own camera there is
    nothing to cut to and the box would promise a cut that cannot
    happen -- so one person alone needs the second camera before this
    says yes.
    """
    named = named_people(pairs)
    return len(named) >= 2 or (len(named) == 1 and cameras >= 2)


def finished_tracks_deeper(base):
    """Look in the subfolders too, "Result" for instance.

    A folder that cannot be read answers like an empty one: whoever
    asks wants finished tracks, and there are none either way.
    """
    if not base or not os.path.isdir(base):
        return None
    try:
        names = sorted(os.listdir(base))
    except OSError:
        return None
    for name in names:
        below = os.path.join(base, name)
        if os.path.isdir(below) and not name.startswith("."):
            hit = finished_tracks_find(below)
            if hit:
                return hit
    return None


def assignment_pairs(voice_rows, assign_rows=()):
    """Every (name, camera) the assignment sheet holds.

    Both levels of it. The voices of a separation carry their own
    camera, and so does a recording that has none underneath it -- a
    clip-on microphone on one camera, say. Reading only the voices hid
    a typed-in single name from the cut altogether: it lives in the
    recording's row, and the cut box asked the wrong list.

    A recording whose voices are on screen answers MIX_ONLY, so it
    falls out again wherever a camera is what counts, and nobody is
    counted twice.
    """
    return ([(nv.get(), cv.get()) for _k, nv, cv in voice_rows]
            + [(nv.get(), cv.get()) for _r, nv, cv in assign_rows])


def cut_title_of(voice_rows, multitrack_on, assign_rows=(), cameras=0):
    """The name the cut box carries, read off the assignment sheet.

    The preview box stands beside it and has to say the same. It read
    "Camera cut -- preview" next to a box called "First cut by speaker"
    until 2.7.0-beta, because the two names were worked out in two
    places.
    """
    return cut_box_title(assignment_pairs(voice_rows, assign_rows),
                         bool(multitrack_on), cameras)


def cut_kind_of(pairs, multitrack_on=False, cameras=0):
    """Which of the three things this cut is: "cameras", "wide", "speakers".

    Between two cameras the picture changes hands and camera cut is the
    right word. On one camera nothing changes hands: what comes of it
    is a cut at every change of speaker, which Resolve can group -- and
    a 360 degree camera gets reframed there, not switched. Calling that
    a camera cut would promise the wrong thing.

    And with one person there is no change of speaker either, so that
    name would promise the wrong thing in its turn. What happens then
    is that their camera stands and the wide shot cuts in, which is
    what the third name says.

    The case is worked out here and nowhere else. The window asks for
    the title of the cut box, the run for the heading in the log, and
    while each of them kept its own reading the third case existed only
    in the window: the log went on calling one person with two cameras
    a first cut by speaker. One thing under two names, and whoever read
    both had to work out that they were the same thing.

    Only the case is shared, not the words. The heading is upper case
    and begins on a fresh line, the title is neither, so a single
    string would have to be mangled at one of the two ends.
    """
    on_camera = set(c for n, c in pairs
                    if (n or "").strip()
                    and c not in (IGNORE_AUDIO, MIX_ONLY))
    # Nothing separated yet says nothing about what will come of it,
    # so the general name stands until the material has answered.
    # And with Multitrack the pairs are not the whole picture: they
    # hold the voices of the separation, while the rows of the
    # assignment table carry cameras of their own that are not in
    # here. Four voices on one camera plus a camera as a track would
    # read as one camera and promise the smaller thing.
    if multitrack_on or not on_camera or len(on_camera) > 1:
        return "cameras"
    if len(named_people(pairs)) < 2 and cameras >= 2:
        return "wide"
    return "speakers"


def cut_box_title(pairs, multitrack_on=False, cameras=0):
    """What the cut box in the window is called."""
    return {"cameras": T('Camera cut'),
            "wide": T('Cut with the wide shot'),
            "speakers": T('First cut by speaker')}[
                cut_kind_of(pairs, multitrack_on, cameras)]


def cut_log_heading(pairs, cameras=0):
    """The same thing as the heading over the log section.

    Upper case and on a fresh line, which is what every heading in the
    log looks like.

    Nobody on a camera at all is the one case the two places read
    differently, and rightly: in the window it means the question has
    not been answered yet and the general name has to stand, here it
    means the answer is no. So it is settled before asking, because
    cut_kind_of cannot tell "not yet" from "never".
    """
    kind = ("speakers" if not named_people(pairs)
            else cut_kind_of(pairs, False, cameras))
    return {"cameras": T('\nCAMERA CUT'),
            "wide": T('\nCUT WITH THE WIDE SHOT'),
            "speakers": T('\nFIRST CUT BY SPEAKER')}[kind]


def multitrack_state_note(tracks, cameras_left):
    """Why Multitrack is not on offer here, in one line, or "".

    The tick stays clickable -- a greyed out control without a reason
    is the dead end this project took out of the preset list on
    24.8.2026, and putting it back at the tick would be the same
    mistake. Instead the line beside it says what is missing, at the
    place where the question is asked rather than at the start button.

    *tracks* is how many rows the assignment table holds that are not
    set aside, *cameras_left* how many cameras could still contribute
    their own audio. Nothing is said where nothing is known yet, and
    nothing where two tracks are there: a line that always stands is
    read as decoration.
    """
    if tracks >= 2:
        return ""
    if not tracks:
        return ""
    if cameras_left:
        return T('One track only -- set a camera\'s Camera audio to '
                 '"use the audio" for a second.')
    return T('One track only, and no camera audio left to take.')


def split_audio_and_video(paths):
    audio, video, other = [], [], []
    for p in paths:
        e = os.path.splitext(p)[1].lower()
        if e in AUDIO_SUFFIXES:
            audio.append(p)
        elif e in VIDEO_SUFFIXES:
            video.append(p)
        else:
            other.append(p)
    return audio, video, other


#---------------------------------------------------------------- Video data

def video_facts(path, fps_default=None, tc_default_value=None):
    d = ffprobe_json(path)
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), None)
    if v is None:
        raise RuntimeError(T('no video track in %s') % os.path.basename(path))
    a = [s for s in d.get("streams", []) if s.get("codec_type") == "audio"]
    fps = fps_default
    if not fps:
        r = v.get("avg_frame_rate") or v.get("r_frame_rate") or "30/1"
        try:
            num, the_one = (int(x) for x in r.split("/"))
            fps = num / the_one if the_one else 30.0
        except Exception:
            fps = 30.0
    tc = tc_default_value
    if tc is None:
        # The tracks before the file, for the reason in file_timecode:
        # the track is the camera's clock, the file level is ffmpeg's
        # reading of it, and the camera wins where they disagree.
        for source in [s.get("tags", {}) or {} for s in d.get("streams", [])] +\
                      [d.get("format", {}).get("tags", {})]:
            if source.get("timecode"):
                tc = source["timecode"]
                break
    dur = float(d.get("format", {}).get("duration") or v.get("duration") or 0.0)
    label_text = 0.0
    try:
        num, the_one = (float(x) for x in str(v.get("r_frame_rate")
                                          or "0/0").split("/"))
        label_text = num / the_one if the_one else 0.0
    except Exception:
        label_text = 0.0
    return {"fps": fps, "tc": tc, "duration": dur, "audio": a, "video": v,
            "width": v.get("width"), "height": v.get("height"),
            "nominal": label_text or fps,
            "tags": (d.get("format") or {}).get("tags") or {}}


#---------------------------------------------------------- Audio analysis

def audio_track_starts_at(path, stream=None):
    """When the first sample of this audio track is to be heard, in seconds.

    A camera track can begin after the picture, and an AAC stream
    begins with samples the file marks as not to be played; both go
    into this number, and both were being thrown away. Measured
    2.9.2026 over three cameras of one shoot: 60,375 ms at one of them
    and none at the other two -- so it is read, never assumed.
    """
    # And what no file declares cannot be put right from here: a stream
    # whose lead-in is nowhere written down comes back that much too
    # late, and nothing in it says by how much.
    try:
        rows = [s for s in (ffprobe_json(path).get("streams") or [])
                if s.get("codec_type") == "audio"]
        row = rows[stream or 0] if rows else {}
        return float(row.get("start_time") or 0.0)
    except (IndexError, TypeError, ValueError):
        return 0.0


def audio_on_the_picture(x, path, rate, stream=None):
    """Put decoded samples where the file says they are to be heard.

    Silence in front where the track starts after the picture, and the
    head cut away where it starts before it. Only for a decode from the
    front: with -ss ffmpeg counts from the presentation time itself and
    the samples already lie right.
    """
    head = int(round(audio_track_starts_at(path, stream) * rate))
    if head > 0:
        return np.concatenate([np.zeros(head, dtype=x.dtype), x])
    if head < 0:
        return x[-head:]
    return x


def decode_audio(path, rate=SR, ss=None, duration=None, stream=None,
                 dtype=None):
    """Decode one channel of a file into samples.

    ffmpeg writes float32 and the default widens it to float64.
    Whoever hands the samples on in float32 asks for float32 here and
    saves a copy at twice the size, which over a whole episode is the
    largest block the program holds. None is that default: numpy is
    fetched at the end of this file and cannot stand in a signature.
    """
    cmd = ["ffmpeg", "-v", "error"]
    if ss is not None:
        cmd += ["-ss", "%.6f" % ss]
    if duration is not None:
        cmd += ["-t", "%.6f" % duration]
    cmd += ["-i", path]
    if stream is not None:
        cmd += ["-map", "0:a:%d" % stream]
    cmd += ["-ac", "1", "-ar", str(rate), "-f", "f32le", "-"]
    p = subprocess.run(cmd, capture_output=True)
    x = np.frombuffer(p.stdout, dtype=np.float32).astype(
        dtype or np.float64)
    # What comes back begins where the file says the track begins, not
    # where ffmpeg's first sample happens to fall. With -ss it already
    # does: there ffmpeg counts from the presentation time itself.
    return x if ss is not None else audio_on_the_picture(x, path, rate,
                                                         stream)


_ENV = {}


def show_progress(text, share=None):
    # Where this thread runs inside a parallel batch, its progress goes into
    # the shared bar rather than onto a line of its own -- three bars above
    # each other would be unreadable.
    own_flag = THREAD_SHARE.get(threading.get_ident())
    if own_flag is not None:
        own_flag.report(0.0 if share is None else share, text)
        return
    step_report(share)
    draw_progress_bar(text, share)


def progress_from_line(line, duration):
    """Extract the progress fraction from a line of "ffmpeg -progress".

    Returns a number between 0 and 0.999, or None if the line says nothing
    about progress. Four places read this output and should read it the same
    way.
    """
    if isinstance(line, bytes):
        line = line.decode("utf-8", "replace")
    line = line.strip()
    if not line.startswith("out_time_ms=") or not duration or duration <= 0:
        return None
    try:
        return min(0.999, int(line.split("=")[1]) / 1e6 / float(duration))
    except ValueError:
        return None


def draw_progress_bar(text, share=None):
    """Write one progress line, directly."""
    if share is None:
        line = "\r  %s" % text
    else:
        line = "\r  %s [%-30s] %3.0f %%" % (text, "#" * int(share * 30),
                                             share * 100)
    if OUTPUT_SINK:
        OUTPUT_SINK(line)
    else:
        sys.stdout.write(line + " " * 6)
        sys.stdout.flush()


class SharedProgressBar(object):
    """One progress bar for everything running at once.

    Every file reports its own share and the average is displayed. Because
    each share can only rise, the bar never jumps back.
    """

    def __init__(self, text, how_many):
        self.text, self.how_many = text, max(1, how_many)
        self.status, self.lock = {}, threading.Lock()
        self.last_time = -1.0
        self.stream = None      # the real output, past the buffer

    def show(self, share):
        line = "\r  %s [%-30s] %3.0f %%" % (
            T('%s (%s files)') % (self.text, group_text(self.how_many)),
            "#" * int(share * 30), share * 100)
        if OUTPUT_SINK:
            OUTPUT_SINK(line)
            return
        # Past the buffer: the bar belongs on the real output, otherwise it
        # only appears once the file is finished.
        stream = self.stream or sys.stdout
        try:
            stream.write(line + " " * 6)
            stream.flush()
        except Exception:
            pass

    def report(self, who, share):
        with self.lock:
            self.status[who] = share
            total = sum(self.status.values()) / float(self.how_many)
            # At most 99 % while the run is not through. The last file reports
            # itself done before its report leaves the buffer, and a bar at 100
            # % with something still arriving below looks like a hang.
            total = min(0.99, total)
            if abs(total - self.last_time) < 0.005:
                return          # nothing new, so no second line
            self.last_time = total
        # The bar in the footer wants the joint figure, not each file's:
        # several threads reporting one at a time would make it jump to
        # whichever file happens to be furthest along.
        step_report(total)
        self.show(total)

    def stop(self):
        self.show(1.0)
        write_through("\n")


class Share(object):
    """The progress of one file, assembled from sections.

    The sections are roughly weighted: measure, write, verify. Within a
    section the ffmpeg progress is passed through. It never goes back.
    """

    def __init__(self, progress_bar, who):
        self.progress_bar, self.who = progress_bar, who
        self.begins, self.until, self.highest = 0.0, 1.0, 0.0
        self.done = set()

    def segment(self, begins, until):
        self.begins, self.until = begins, until
        self.report(0.0)

    def report(self, share, text=None):
        # The bar itself runs jointly; every step still enters this file's
        # report as soon as it is through. Otherwise the lines one knows from a
        # sequential run would be missing there.
        if text and share >= 0.999 and text not in self.done:
            self.done.add(text)
            write_through("  %s [%s] 100 %%\n" % (text, "#" * 30))
        value = self.begins + (self.until - self.begins) * max(0.0, min(1.0, share))
        if value > self.highest:
            self.highest = value
        self.progress_bar.report(self.who, self.highest)


# The run says which stage it is in, and how far that stage is. The
# interface draws one bar out of it; on the command line nothing is
# connected and the calls cost a comparison.
PROGRESS_SINK = None
_STEP = {"name": ""}


def step_begin(name):
    """Say that the run has reached a stage. Ends the one before it."""
    _STEP["name"] = name
    if PROGRESS_SINK:
        try:
            PROGRESS_SINK(name, None)
        except Exception:
            pass


def step_report(share):
    """Say how far the current stage is, 0 to 1."""
    if PROGRESS_SINK and _STEP["name"] and share is not None:
        try:
            PROGRESS_SINK(_STEP["name"], float(share))
        except Exception:
            pass


def run_stages(multitrack, cameras, auphonic, speakers=None):
    """The stages of a run and what share of the bar each is worth.

    The weights are proportions measured on real jobs, not guesses at a
    clock: writing the camera files reads and re-encodes every camera in
    full and takes longer than everything before it together, so it gets
    most of the bar. Pulling the audio out of the cameras is the other
    long one. A stage that will not happen is not in the list.
    """
    cameras = max(0, int(cameras))
    out = [("plan", 1.0, T('Reading the plan'))]
    # Only the multitrack path pulls the audio out of the cameras; the
    # simple path aligns against them and leaves them alone. Listed for
    # both, the bar held a fifth of itself for a stage that never
    # reported, and then jumped that fifth in one go when the next one
    # began.
    if cameras and multitrack:
        out.append(("camera audio", 5.0 * cameras,
                    T('Audio out of the cameras')))
    out.append(("time base", 4.0, T('Common time axis')))
    if auphonic:
        out.append(("auphonic", 8.0, T('Processing at auphonic.com')))
    else:
        out.append(("loudness", 4.0, T('Loudness and levels')))
    if multitrack if speakers is None else speakers:
        out.append(("speakers", 3.0, T('Who speaks when')))
    if cameras:
        out.append(("cameras", 12.0 * cameras,
                    T('Writing the camera files')))
    out.append(("result", 1.0, T('Handover and result')))
    return out


class ProgressPlan(object):
    """One bar for a job whose steps take very different lengths.

    Each step carries a weight, and the bar is the weighted sum of what
    the steps report. Three things make it readable rather than merely
    correct:

    It never goes back. A step added while the job runs lowers the
    arithmetic, and a bar jumping backwards reads as a fault even though
    nothing was lost.

    A step that cannot say how far it is creeps towards its own end
    instead of standing still. The creep slows as it approaches and
    never reaches the boundary, so the bar keeps moving without ever
    claiming a step is further along than it is.

    Long steps get room in proportion to how long they take. Pulling the
    audio out of an hour of 4K and reading a wav file are one step each,
    and giving them the same share of the bar would make it useless.
    """

    def __init__(self):
        self.order = []
        self.weight = {}
        self.share = {}
        self.real = {}
        self.caption = {}
        self.began = set()
        self.highest = 0.0

    def clear(self):
        self.__init__()

    def add(self, name, weight=1.0, caption=""):
        """Announce a step. Announcing it twice changes nothing."""
        if name not in self.weight:
            self.order.append(name)
            self.weight[name] = max(0.01, float(weight))
            self.share[name] = 0.0
        if caption:
            self.caption[name] = caption

    def begin(self, name, caption="", weight=1.0):
        """Mark a step as under way without claiming a figure for it.

        For work that reports nothing at all until it is finished. Such
        a step may creep the whole way to its ceiling; one that does
        report stays close to what it reported.
        """
        self.add(name, weight, caption)
        self.began.add(name)

    def report(self, name, share, caption=""):
        """Say how far one step is. Unknown steps count as weight 1."""
        self.begin(name, caption)
        value = max(0.0, min(1.0, float(share)))
        self.real[name] = max(self.real.get(name, 0.0), value)
        self.share[name] = max(self.share[name], value)

    def done(self, name):
        self.report(name, 1.0)

    def drop(self, names):
        """Forget steps whose work was called off.

        A step left standing half way is neither finished nor being
        worked on, and it holds the bar up for ever. Marking it done
        instead would put the bar at the end of work nobody did.
        """
        for name in list(names):
            if name not in self.weight:
                continue
            self.order.remove(name)
            del self.weight[name]
            del self.share[name]
            self.real.pop(name, None)
            self.caption.pop(name, None)
            self.began.discard(name)
        if not self.order:
            self.highest = 0.0

    def creep(self, seconds, reach=0.93, half_life=30.0, lead=0.12,
              beyond=0.99, slower=10.0):
        """Let the running steps drift on, but not into a lie.

        Asymptotic: half the remaining distance every half_life. A step
        that has reported a figure may only creep a little past it --
        otherwise the bar would sit near the end of a step that is a
        tenth of the way through. A step that reports nothing at all has
        nothing to be held to and may creep the whole way.

        Past the ceiling it goes on at a tenth of the speed, up to
        *beyond*. Something that runs far longer than expected should
        still show life; at a tenth of the pace that reads as "nearly
        there, still working" rather than as a promise.
        """
        if seconds <= 0 or half_life <= 0:
            return
        part = 1.0 - 0.5 ** (float(seconds) / float(half_life))
        crawl = 1.0 - 0.5 ** (float(seconds) / (float(half_life) * slower))
        for name in self.began:
            here = self.share[name]
            top = (reach if name not in self.real
                   else min(reach, self.real[name] + lead))
            # A hair short of the ceiling counts as at it. The approach
            # is asymptotic and would otherwise never cross, so the slow
            # stretch past it could never be reached at all.
            if here < top - 0.001:
                self.share[name] = here + (top - here) * part
            elif top >= reach and here < beyond:
                here = max(here, top)
                self.share[name] = here + (beyond - here) * crawl

    def total(self):
        """The whole job as one number, 0 to 1, and never falling."""
        weight = sum(self.weight.values())
        if not weight:
            return self.highest
        now = sum(self.weight[n] * self.share[n] for n in self.order) / weight
        self.highest = max(self.highest, now)
        return self.highest

    def busy(self):
        """Report whether anything is still outstanding."""
        return any(self.share[n] < 0.999 for n in self.order)

    def running(self):
        """The steps under way, in the order they were announced."""
        return [n for n in self.order
                if n in self.began and self.share[n] < 0.999]

    def line(self):
        """One line for beside the bar: what is being worked on."""
        busy = self.running()
        if not busy:
            return ""
        first = self.caption.get(busy[0]) or busy[0]
        if len(busy) == 1:
            return first
        return T('%s and %s more') % (first, group_text(len(busy) - 1))


def write_through(text):
    """Print text; buffer it first when running in a parallel thread."""
    p = THREAD_BUFFER.get(threading.get_ident())
    if p is not None:
        p.append(text)
        return
    if OUTPUT_SINK:
        OUTPUT_SINK(text)
    else:
        sys.stdout.write(text)
        sys.stdout.flush()


class ThreadOutput(object):
    """Stand-in for sys.stdout while several threads are writing."""

    def __init__(self, real):
        self.real = real

    def write(self, text):
        p = THREAD_BUFFER.get(threading.get_ident())
        if p is not None:
            p.append(text)
            return len(text)
        return self.real.write(text)

    def flush(self):
        try:
            self.real.flush()
        except Exception:
            pass


def decode_audio_long(path, rate, duration, text, stream=None, report=None):
    """Decode audio with progress reporting.

    Reading a 30 GB file once takes minutes, and a blinking cursor is not
    enough feedback for that.
    """
    return decode_audio_tracks(path, rate, duration, text, [stream],
                               report)[0]


def decode_audio_tracks(path, rate, duration, text, streams, report=None):
    """Decode several tracks of one file in one pass over the container.

    Asking track by track reads a 36 GB camera file once per track, and
    off a drive that pass is the whole of the waiting; one ffmpeg with a
    -map per track reads it once. One process has one progress stream,
    so the text has to name every track that pass is fetching.
    """
    cmd = ["ffmpeg", "-v", "error", "-nostats", "-progress", "pipe:1",
           "-i", path]
    raws = []
    for stream in streams:
        fd, raw = tempfile.mkstemp(suffix=".raw")
        os.close(fd)
        raws.append(raw)
        if stream is not None:
            cmd += ["-map", "0:a:%d" % stream]
        cmd += ["-ac", "1", "-ar", str(rate), "-f", "f32le", "-y", raw]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
        points = 0
        for line in proc.stdout:
            share = progress_from_line(line, duration)
            if share is not None:
                if report:
                    report(share)
                else:
                    show_progress(text, share)
                continue
            note = line.decode("utf-8", "replace").strip()
            if note.startswith("out_time_ms=") or note.startswith("frame="):
                points = (points + 1) % 20
                if not report:
                    show_progress(note + " " + "." * (points // 4 + 1))
        proc.wait()
        if report:
            report(1.0)
        else:
            show_progress(text, 1.0)
            if THREAD_SHARE.get(threading.get_ident()) is None:
                if OUTPUT_SINK:
                    OUTPUT_SINK("\n")
                else:
                    sys.stdout.write("\n")
        # Each track on the time of its own start, the same as the
        # short way above: a big file must not be placed differently
        # from a small one only because it came through here.
        return [audio_on_the_picture(
                    np.fromfile(raw, dtype=np.float32).astype(np.float64),
                    path, rate, stream)
                for raw, stream in zip(raws, streams)]
    finally:
        for raw in raws:
            remove_quietly(raw)




def running_from():
    """Which copy of the script this is.

    Not sys.argv[0]: the restart after an update and the call out of
    DaVinci Resolve both set it to something else. __file__ is the file
    that was really loaded.
    """
    try:
        return os.path.abspath(__file__)
    except Exception:
        return "?"





# The mark the window's own lines carry, so they can be picked out of a
# log that also holds what ffmpeg and Qt write: grep for it.
GUI_MARK = "[GUI]"


# What a speaker reading leaves behind in the state. Cleared together,
# or a reading of one project is read back in the next.
SPEAKER_STATE = ("measure_failed", "speakers_measured", "speakers_measuring")


def speakers_still_wanted(state):
    """Whether the speakers still have to be worked out.

    Not while one run is under way and not after one failed -- it would
    fail the same way and cost the same minutes. And not where a
    finished run already knows them: measuring again would relabel its
    preview as measured from the raw recordings.
    """
    return not (state.get("speakers_measured")
                or state.get("speakers_measuring")
                or state.get("measure_failed")
                or state.get("cut_basis") in ("run", "auphonic"))


# How close a player has to be to a jump before it counts as arrived.
# One second: a seek lands on the key frame before the mark, and with
# long GOPs on 4K material that is most of a second away.
SPOT_ARRIVED_MS = 1000

# Waiting for a jump to land, as the cut player's Seeker does -- which
# is why that one switches cameras cleanly. Measured on 18 and 27 GB
# files: a file falls back to its front 18 to 88 ms after reporting
# itself loaded. A seek is a request, not a command.
SEEK_HIT_MS = 350
SEEK_AGAIN_MS = 120
SEEK_PATIENCE_S = 5.0
SEEK_SETTLE_S = 0.5


def gui_log(text):
    """Write down what the window just did.

    A window tells nobody afterwards what it was showing, where it
    stood, or which of the two reckonings a position came out of. The
    log is what somebody can send along with a complaint. It lands in
    the file: redirect_console has the descriptors by then.
    """
    print("%s %s  %s" % (GUI_MARK, time.strftime("%H:%M:%S"), text))




def outside_what(cmd):
    """The tool and the file one call to another program is about."""
    parts = [str(x) for x in ([cmd] if isinstance(cmd, str) else (cmd or []))]
    if not parts:
        return "", ""
    tool = os.path.basename(parts[0])
    # A python of its own runs the speaker separation, and "python3"
    # says nothing about what is taking the minutes. The script it is
    # given is the name worth printing.
    if tool.startswith("python") and len(parts) > 1:
        tool = os.path.basename(parts[1]).replace(".py", "") or tool
    for i, one in enumerate(parts):
        if one == "-i" and i + 1 < len(parts):
            return tool, os.path.basename(parts[i + 1])
    # ffprobe takes its file last and without a switch in front of it.
    tail = parts[-1]
    return tool, os.path.basename(tail) if not tail.startswith("-") else ""












# Otherwise the last run of identical calls is never written: nothing
# different comes after it to push it out.
atexit.register(outside_flush)


def outside_log(cmd, seconds=None):
    """Write down one call to a program outside this one.

    Every call is here because subprocess is wrapped once below, so a
    new call site cannot forget to say so.
    """
    tool, about = outside_what(cmd)
    if tool:
        outside_say(tool, about, seconds)


@contextlib.contextmanager
def outside_work(tool, about):
    """Time work that runs in this process but costs like an outside call.

    The models are not subprocesses, so the wrapper below does not see
    them -- and they are the longest thing a run does. Said even where
    it fails: work that broke off after four minutes still took them.
    """
    began = time.monotonic()
    try:
        yield
    finally:
        outside_say(tool, about, time.monotonic() - began)


_subprocess_run, _subprocess_popen = subprocess.run, subprocess.Popen


# run() opens a Popen of its own, so without this every call it makes
# would be said twice. Per thread: the window runs its prework in
# several at once, and one counter for all of them would silence the
# wrong lines.
_in_run = threading.local()


def run_outside(cmd, *rest, **named):
    """subprocess.run, with the call and how long it took written down."""
    began = time.monotonic()
    _in_run.here = getattr(_in_run, "here", 0) + 1
    try:
        return _subprocess_run(cmd, *rest, **named)
    finally:
        _in_run.here -= 1
        outside_log(cmd, time.monotonic() - began)


class SaysWhenDone(_subprocess_popen):
    """A Popen that says how long it ran when somebody waits for it.

    Started and finished are two lines because a long call is
    interesting while it runs -- and without the second one a process
    that took four minutes cannot be told from one that took four
    seconds.
    """

    def __init__(self, cmd, *rest, **named):
        self._began = time.monotonic()
        self._said = False
        self._cmd = cmd
        _subprocess_popen.__init__(self, cmd, *rest, **named)

    def _say_done(self):
        if not self._said:
            self._said = True
            outside_log(self._cmd, time.monotonic() - self._began)

    def wait(self, *rest, **named):
        try:
            return _subprocess_popen.wait(self, *rest, **named)
        finally:
            self._say_done()

    def communicate(self, *rest, **named):
        try:
            return _subprocess_popen.communicate(self, *rest, **named)
        finally:
            self._say_done()


def popen_outside(cmd, *rest, **named):
    """subprocess.Popen, saying both when it started and when it ended."""
    if getattr(_in_run, "here", 0):
        return _subprocess_popen(cmd, *rest, **named)
    outside_log(cmd)
    return SaysWhenDone(cmd, *rest, **named)


def watch_outside_calls():
    """Route every call to another program past the log.

    Wrapped here rather than at the 46 call sites: what is asked of a
    call site is forgotten by the next one somebody writes. Called from
    main(), where somebody has asked for a run -- done while the file
    is read, the replacement would reach into whoever imported it, and
    their processes have nothing to do with a run.
    """
    subprocess.run = run_outside
    subprocess.Popen = popen_outside


def trouble_log(text):
    """Write down what the window is showing in red.

    A red mark in the window is gone the moment the row is drawn
    again, and the complaint about it arrives hours later. In the log
    it keeps, with the time beside it.
    """
    said = " ".join(str(text or "").split())
    if said:
        log_aside("%s %s  %s"
                  % (BAD_MARK, time.strftime("%H:%M:%S"), said[:200]))


def redirect_console():
    """Redirect everything that would go to the terminal into a file.

    Not only our own messages: the file descriptors themselves are
    redirected so that what Qt and ffmpeg write underneath Python comes
    along. One backup of the previous run is kept.
    """
    file_path = log_path()
    if not file_path:
        return None
    # The aside handle may already stand open on the file about to be
    # renamed -- the tool check runs a process before this, and every
    # outside call is written down. Left alone, the whole run's aside
    # lines would land in the previous run's log. Measured 4.9.2026.
    while _LOG_ASIDE:
        kept = _LOG_ASIDE.pop()
        try:
            if kept is not None:
                kept.close()
        except Exception:
            kept = None
    # The backup is called ..._1.log rather than ....log.1 --
    # otherwise Finder does not know the extension and will not open it.
    before_value = os.path.splitext(file_path)[0] + "_1.log"
    try:
        old = file_path + ".1"
        if os.path.exists(old):
            os.unlink(old)          # from older versions
    except OSError:
        pass
    try:
        if os.path.exists(file_path):
            os.replace(file_path, before_value)
        file = open(file_path, "w", buffering=1, encoding="utf-8",
                     errors="replace")
        # Header: version, time, machine -- and which copy of the
        # script this was. Several runnable copies of the same version
        # are the normal case here: the snapshot the test suite runs
        # against, the .old the self-update leaves behind, the download
        # in the Downloads folder. They share one log file, and without
        # the path nobody can tell later why one run came out different
        # from another.
        file.write("Video Podcast Magic %s   %s   %s %s   %s\n%s\n\n"
                    % (VERSION,
                       time.strftime("%Y-%m-%d %H:%M:%S"),
                       platform.system(), platform.release(),
                       python_note(), running_from()))
        os.dup2(file.fileno(), 1)
        os.dup2(file.fileno(), 2)
        # The aside lines go through this same handle from now on: two
        # handles on one file keep two write positions, and whichever
        # is behind writes over what the other put there. Measured
        # 5.9.2026 -- a line came out as "rogram list is settled".
        _LOG_ASIDE.append(file)
    except Exception:
        return None
    return file_path


def envelope_cache_folder():
    """Return the folder the computed envelopes may live in."""
    return cache_folder("envelopes")
















def clean_envelope_cache(days=30):
    """Discard stale envelopes; once per run is enough."""
    clean_old_files(envelope_cache_folder(), days)




_RECIPE_MARKS = {}


def recipe_mark(name, *work):
    """A short mark of the way something is worked out.

    A number counted by hand would have to be remembered, and the day
    somebody forgets it the store hands back a measurement another
    recipe wrote. So the source of the functions that decide the
    numbers is read and hashed: it cannot change without changing
    this.
    """
    if name not in _RECIPE_MARKS:
        try:
            import inspect
            text = "".join(inspect.getsource(f) for f in work)
        except Exception:
            # Nothing to read the source from. The version is coarse --
            # every release throws the store away -- but it never hands
            # back what some other recipe wrote.
            text = VERSION
        _RECIPE_MARKS[name] = hashlib.sha1(
            text.encode("utf-8")).hexdigest()[:12]
    return _RECIPE_MARKS[name]


def envelope_recipe_mark():
    """The mark for a curve: what ffmpeg is asked for, and the rest."""
    return recipe_mark("envelope", decode_audio, decode_audio_tracks,
                       envelope, audio_track_starts_at,
                       audio_on_the_picture)


def envelope_cache_path(path, hop_ms, rate):
    """Return a cache name that changes as soon as the file changes.

    Or as soon as the way the curve is worked out changes: without that
    mark a changed recipe reads the old curves back and the run
    compares two of them that were never measured the same way.
    """
    folder = envelope_cache_folder()
    if not folder:
        return None
    try:
        st = os.stat(path)
    except OSError:
        return None
    import hashlib
    fingerprint = "%s|%d|%d|%.3f|%d|%s" % (path_key(path), int(st.st_mtime),
                                    st.st_size, hop_ms, rate,
                                    envelope_recipe_mark())
    return os.path.join(folder,
                        hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()
                        + ".npy")


def envelope_log(path, hop_ms, rate, what):
    """Say whether a curve came out of the store or off the disc.

    A curve costs minutes on a large file and nothing when it is
    found. Which of the two happened is invisible from outside, and
    the numbers are in the line because a curve is kept under them:
    the same file at another hop or rate is another curve.
    """
    log_aside("%s %s  %-30s %g/%d  %s"
              % (ENV_MARK, time.strftime("%H:%M:%S"),
                 os.path.basename(path)[:30], hop_ms, rate, what))


def video_envelope(path, hop_ms=5.0, rate=4000, report=None):
    """Return the envelope of the video audio track, computed once per file.

    The cache survives the whole run. The interface warms it while the user
    is still typing, so by the time the run starts the curve is there.
    Kept under path_key: the prework warms it under the absolute path
    and the time axis asks under the name the file dialog gave, and
    where those differ the file was read twice. It is opened by the
    path as it came in."""
    api_key = (path_key(path), hop_ms, rate)
    if api_key not in _ENV:
        # Reading an hour of 4K takes minutes; twice is unnecessary.
        cache = envelope_cache_path(path, hop_ms, rate)
        if cache and os.path.exists(cache):
            try:
                _ENV[api_key] = np.load(cache)
                envelope_log(path, hop_ms, rate, "read back from the store")
                return _ENV[api_key]
            except Exception as trouble:
                envelope_log(path, hop_ms, rate,
                             "the stored curve would not read: %s" % trouble)
        else:
            envelope_log(path, hop_ms, rate,
                         "nothing in the store, reading the file"
                         if cache else "no store to look in")
        duration = 0.0
        try:
            duration = float(ffprobe_json(path).get("format", {}).get("duration") or 0)
        except Exception:
            pass
        large = os.path.getsize(path) > 200e6 if os.path.exists(path) else False
        if large or report:
            x = decode_audio_long(path, rate, duration,
                                T('Reading audio track from %s') % os.path.basename(path),
                                report=report)
        else:
            x = decode_audio(path, rate=rate)
        _ENV[api_key] = envelope(x, hop_ms, rate)
        if len(_ENV[api_key]) < 10:
            # ffmpeg delivered nothing. Caching that would mean treating the
            # file as unalignable until it next changes, without ever saying
            # why.
            _ENV.pop(api_key, None)
            raise ValueError(T('no audio data from %s')
                             % os.path.basename(path))
        if cache:
            # Beside it and then moved: two files being measured at
            # once, or a run broken off, must not leave half a curve
            # behind for the next start to read as a measurement.
            try:
                # The suffix has to be .npy: np.save appends one
                # otherwise, and the move would then miss the file.
                fd, beside = tempfile.mkstemp(dir=os.path.dirname(cache),
                                              prefix=".vpm_", suffix=".npy")
                os.close(fd)
                np.save(beside, _ENV[api_key].astype("float32"))
                os.replace(beside, cache)
            except Exception:
                pass
    return _ENV[api_key]


def envelope(x, hop_ms=5.0, rate=SR):
    h = max(1, int(hop_ms * rate / 1000.0))
    m = len(x) // h
    if m < 2:
        return np.zeros(0)
    e = np.sqrt((x[:m * h].reshape(-1, h) ** 2).mean(1))
    e = np.log(e + 1e-9)
    return e - e.mean()


# Narrow where mains hum sits, wider above it. Everything over the last
# edge is counted into the last band: at 4000 Hz that is a single bin.
BAND_EDGES = (0, 50, 75, 100, 125, 150, 200, 250, 300, 400, 500, 650,
              800, 1000, 1200, 1400, 1600, 1800, 2000)
# How long a stretch one band level is read over. 64 ms is long enough
# to tell 50 Hz from 100 Hz; the 5 ms box the plain curve uses is not,
# and there a hum and the voice over it land in the same value.
BAND_WINDOW_S = 0.064
# A band counts if its own loudness moves at least half as much as the
# liveliest band of that recording. Measured 1.9.2026 over 38 tracks
# from four productions: the mains hum drops out of every one of them,
# and none of the 85 pairs that belong together got worse.
BAND_MOVES_ENOUGH = 0.5


def band_powers(x, hop_ms=5.0, rate=SR):
    """How much power each band holds at every step of the curve.

    One short spectrum every hop, its bins summed inside the band
    edges. Worked through in blocks: a whole episode at once is a
    matrix of some gigabytes, and the answer is the same either way.
    """
    hop = max(1, int(hop_ms * rate / 1000.0))
    win = max(16, 1 << int(round(np.log2(BAND_WINDOW_S * rate))))
    steps = (len(x) - win) // hop
    bands = len(BAND_EDGES) - 1
    if steps < 10:
        return np.zeros((bands, 0), dtype=np.float32)
    which = np.clip(np.searchsorted(np.asarray(BAND_EDGES, float),
                                    np.fft.rfftfreq(win, 1.0 / rate),
                                    side="right") - 1, 0, bands - 1)
    shape = np.hanning(win)
    out = np.empty((bands, steps), dtype=np.float32)
    block = 40000
    for s in range(0, steps, block):
        k = min(block, steps - s)
        at = np.arange(win)[None, :] + hop * np.arange(s, s + k)[:, None]
        power = np.abs(np.fft.rfft(x[at] * shape, axis=1)) ** 2
        for b in range(bands):
            here = which == b
            out[b, s:s + k] = power[:, here].sum(1) if here.any() else 0.0
    return out


def moving_bands(power):
    """Which bands say something about the time, and which stand still.

    A band whose level never changes cannot place anything, however
    loud it is: mains hum sits there at full strength and says the
    same thing from the first second to the last. Asked of the
    recording itself, so no frequency has to be set from outside.
    """
    if not power.size:
        return np.zeros(len(power), dtype=bool)
    move = np.array([float(np.log(np.sqrt(np.asarray(p, float)) + 1e-9).std())
                     for p in power])
    return move >= BAND_MOVES_ENOUGH * (float(move.max()) or 1.0)


def band_envelope(x, hop_ms=5.0, rate=SR):
    """The loudness curve without the bands that carry no movement.

    What envelope() reads in one piece, read band by band with the
    still ones left out. Where every band moves alike nothing is left
    out, and this is the same curve through a longer window.
    """
    power = band_powers(x, hop_ms, rate)
    keep = moving_bands(power)
    kept = power[keep] if keep.any() else power
    if not kept.size:
        return np.zeros(0)
    e = np.log(np.sqrt(kept.astype(np.float64).sum(0)) + 1e-9)
    return e - e.mean()


def phase_align(a, b, rate, most_s=None):
    """Where b sits against a, by phase alone. (seconds, sharpness).

    The envelope way asks where two recordings are loud together, and
    that needs something to be loud and quiet about. Music has almost
    nothing: a mixed, limited song holds the same loudness for minutes.
    Measured on 23.8.2026 -- an iPhone recording of monitor speakers
    against the finished mix of the same music -- the envelope way
    answered 74.775 s at a quality of -0.183, and the right answer was
    569.2 s.

    This one throws the loudness away and keeps only the phase, which
    is what a re-recording through a room survives. It found that 569.2
    s to within twelve milliseconds, first try, with nothing to go on.

    The sharpness is the peak against the noise around it. It says how
    much the answer is worth, and it is the only thing that does: a
    peak that is barely above its neighbours is a guess.
    """
    if len(a) < rate or len(b) < rate:
        return 0.0, 0.0
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    fa = np.fft.rfft(np.asarray(a, float) - np.mean(a), n)
    fb = np.fft.rfft(np.asarray(b, float) - np.mean(b), n)
    both = fb * np.conj(fa)
    # The whitening is the whole point: every frequency counts the
    # same, so a loud bass drum does not drown out the rest.
    line = np.fft.irfft(both / (np.abs(both) + 1e-12), n)
    k = int(np.argmax(line))
    if k > n // 2:
        k -= n
    if most_s is not None and abs(k) / float(rate) > most_s:
        return 0.0, 0.0
    sharp = float(line.max() / (line.std() or 1.0))
    return k / float(rate), sharp


def looks_like_music(env):
    """A guess at whether this is music, for the log and nothing else.

    Speech swings in syllables, two to eight times a second. Music
    swings with the beat and the phrase, slower. Measured on 23.8.2026
    the two do not separate cleanly -- a finished mix landed at 26 per
    cent of its movement in the syllable band, speech at 31 to 32 --
    so this decides nothing. It only explains, afterwards, why the
    plain way had so little to work with.
    """
    e = np.asarray(env, float)
    e = e[np.isfinite(e)]
    if len(e) < 4000:
        return False
    e = e - e.mean()
    power = np.abs(np.fft.rfft(e * np.hanning(len(e)))) ** 2
    hz = np.fft.rfftfreq(len(e), 0.005)
    whole = float(power[(hz >= 0.2) & (hz < 20.0)].sum()) or 1.0
    syllables = float(power[(hz >= 2.0) & (hz < 8.0)].sum()) / whole
    return syllables < 0.20


def cross_correlate(a, b):
    """Where b sits against a, and how well it fits there.

    The peak is the largest positive one, not the largest by size.
    An envelope here is log loudness with its mean taken out, so it
    swings either side of zero -- but two that belong together still
    rise and fall together, and that pushes the correlation up. A
    strong negative peak is the opposite: loud where the other is
    quiet. That is never where they belong, however large it is.

    Taking the absolute value used to hand exactly that back. Measured
    on 23.8.2026, an iPhone recording of monitor speakers against the
    finished mix of the same music: it answered +74.775 s at -0.183,
    while the best real agreement was +0.131 somewhere else again.
    Neither is a match -- but only one of the two is even a possible
    one. The right answer, +569.2 s, needed another method entirely.
    """
    m = min(len(a), len(b))
    if m < 10:
        return 0, 0.0
    a, b = a[:m], b[:m]
    nf = 1 << int(np.ceil(np.log2(2 * m)))
    cc = np.fft.irfft(np.fft.rfft(b, nf) * np.conj(np.fft.rfft(a, nf)), nf)
    k = int(np.argmax(cc))
    if k > nf // 2:
        k -= nf
    label_text = np.sqrt((a ** 2).sum() * (b ** 2).sum())
    return k, float(cc[k % nf] / label_text) if label_text else 0.0


def join_with_report(paths, target, keep_parts=False):
    """Join the blocks of one recording and say what was found.

    The joining was shared; the reporting was not. The ordinary path
    said how many blocks went together, where the gaps were and whether
    two of them overlapped instead of following each other. The
    multitrack path did the same work in silence, so a recording with a
    ten-second hole in it went through without a word.
    """
    source, join_info = join_audio_parts(paths, target, keep_parts=keep_parts)
    if join_info.get("tc"):
        print(T('  %s blocks joined via timecode, start %s')
              % (group_text(join_info["blocks"]),
                 timecode_string(join_info["start"] / float(SR))))
        for at_s, g in join_info.get("gaps_found", []):
            if g > 0:
                print(T('  Gap of %s at %s -- filled with silence')
                      % (as_hms(g / float(SR)), as_hms(at_s / float(SR))))
            else:
                # A negative gap is an overlap. Nothing is filled there;
                # the two sound at the same time.
                print(T('  Overlap of %s at %s -- both sound there')
                      % (as_hms(-g / float(SR)), as_hms(at_s / float(SR))))
        if join_info.get("side_by_side"):
            print(T('  They overlap -- several microphones at once, not '
                    'blocks in a row.'))
            if join_info.get("parts"):
                print(T('  Each one also goes into the video as a track of '
                        'its own: %s')
                      % ", ".join(n for n, _p in join_info["parts"]))
            else:
                print(T('  Only the mix goes into the video '
                        '(--no-single-tracks).'))
    else:
        print(T('  %s blocks joined in name order (no timecode -- gaps '
                'would not be recognisable)')
              % group_text(join_info["blocks"]))
    return source, join_info


def join_audio_parts(paths, target, keep_parts=False):
    """Join several audio files into one.

    With timecodes they are placed on a common time axis and gaps are filled
    with silence. Without, they are laid end to end in the order they came
    in -- the caller has already put them in it.

    The result has as many channels as the widest of them. One stereo
    recording among mono ones therefore keeps its sides, and the mono ones
    are copied to both -- written out rather than left to ffmpeg, which
    would take 3 dB off them on the way.

    With *keep_parts* each recording is also written on its own, on the same
    axis and the same length as the sum, so it can go into the video beside
    the mix. Only where the recordings overlap: blocks laid end to end are
    one recording, and a track per block would be silence with one block in
    it. It costs no second decode -- the same pass writes both.
    """
    paths = list(paths)
    if len(paths) == 1:
        return paths[0], {"blocks": 1, "parts": []}
    channels = widest_track(paths)
    same = [channel_filter(kept_channels(p), channels) for p in paths]
    lengths = [sample_count(p) for p in paths]
    trs = [bext_time_reference(p) for p in paths]
    # Every file has to carry a time, and no two may claim the same one:
    # sorting by it would otherwise depend on the order the files came in.
    # Two recorders started together write exactly the same number, and
    # those recordings run at the same time -- so they are placed on the
    # axis together rather than end to end.
    having_tc = all(t is not None for t in trs)
    if having_tc and len(set(trs)) != len(trs):
        order = sorted(range(len(paths)),
                       key=lambda i: (trs[i], os.path.basename(paths[i]).lower()))
        paths = [paths[i] for i in order]
        lengths = [lengths[i] for i in order]
        trs = [trs[i] for i in order]
        same = [same[i] for i in order]

    if having_tc:
        entries = list(zip(trs, paths, lengths)) if len(set(trs)) != len(trs) \
            else sorted(zip(trs, paths, lengths))
        t0 = entries[0][0]
        total = max(t + n for t, _, n in entries) - t0
        gaps = []
        for (ta, _, na), (tb, _, _) in zip(entries, entries[1:]):
            g = tb - (ta + na)
            if abs(g) > SR // 100:
                gaps.append((ta + na - t0, g))
        # Do the recordings run at the same time or one after another? The
        # timecodes say so, and nothing else has to be guessed: overlapping
        # means several microphones were running at once, and then each one
        # is worth a track of its own.
        side_by_side = any(tb < ta + na for (ta, _, na), (tb, _, _)
                           in zip(entries, entries[1:]))
        alone = []
        if side_by_side and keep_parts:
            folder = os.path.dirname(os.path.abspath(target)) or "."
            for i, (_t, p, _n) in enumerate(entries):
                alone.append((guess_speaker_name(p),
                              os.path.join(folder, "part%d_%s.wav"
                                           % (i, safe_filename(
                                               guess_speaker_name(p))))))
        parts, chains, markers, writes = [], [], [], []
        for i, (t, p, n) in enumerate(entries):
            parts += ["-i", p]
            d = t - t0
            f = [channel_filter(kept_channels(p), channels)]
            f += ["adelay=delays=%dS:all=1" % d] if d else []
            f += ["apad=whole_len=%d" % total, "atrim=end_sample=%d" % total,
                  "asetpts=N/SR/TB"]
            # One decode, two uses: the sum, and the single track beside it.
            # A filter output can only be read once, hence the split.
            tail = ",asplit=2[t%d][s%d]" % (i, i) if alone else "[t%d]" % i
            chains.append("[%d:a]%s%s" % (i, ",".join(f), tail))
            markers.append("[t%d]" % i)
            if alone:
                writes += (["-map", "[s%d]" % i, "-c:a", "pcm_s24le",
                            "-write_bext", "1", "-metadata",
                            "time_reference=%d" % t0]
                           + wav_safe(alone[i][1])
                           + ["-y", alone[i][1]])
        fc = ";".join(chains) + ";" + "".join(markers) +\
             "amix=inputs=%d:normalize=0[out]" % len(markers)
        shell_quote(["ffmpeg", "-v", "error"] + parts + ["-filter_complex", fc,
            "-map", "[out]", "-c:a", "pcm_s24le", "-write_bext", "1",
            "-metadata", "time_reference=%d" % t0]
            + wav_safe(target) + ["-y", target] + writes)
        return target, {"blocks": len(paths), "tc": True, "gaps_found": gaps,
                      "start": t0, "side_by_side": side_by_side,
                      "parts": alone}

    # In the order they came in. Without a timecode that order is the
    # only one there is: it comes from the counter, from the clock in the
    # name, or from a hand that said these belong together in this order.
    # Sorting by name again would throw the last of the three away.
    row = list(zip(paths, lengths))
    if len(set(same)) == 1 and same[0] == "anull":
        # All alike: the concat demuxer is the cheapest way and needs no
        # filter graph at all.
        lst = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
        for p, _ in row:
            lst.write("file '%s'\n" % os.path.abspath(p).replace("'", "'\\''"))
        lst.close()
        try:
            shell_quote(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0",
                "-i", lst.name, "-c:a", "pcm_s24le", "-y", target])
        finally:
            os.unlink(lst.name)
        return target, {"blocks": len(paths), "tc": False, "parts": []}
    # Different channel counts: the concat demuxer refuses those, so the
    # blocks are brought to the same width first and strung together in the
    # filter graph.
    parts, chains, markers = [], [], []
    for i, (p, _n) in enumerate(row):
        parts += ["-i", p]
        chains.append("[%d:a]%s[t%d]"
                      % (i, channel_filter(kept_channels(p), channels), i))
        markers.append("[t%d]" % i)
    fc = ";".join(chains) + ";" + "".join(markers) +\
        "concat=n=%d:v=0:a=1[out]" % len(markers)
    shell_quote(["ffmpeg", "-v", "error"] + parts + ["-filter_complex", fc,
        "-map", "[out]", "-c:a", "pcm_s24le", "-y", target])
    return target, {"blocks": len(paths), "tc": False, "parts": []}


def audio_range_covered_by_video(audio, video, edge_s=60.0):
    """Return which part of the audio file has a counterpart in the picture.

    Only the first and last *edge_s* seconds are searched. Two passes:
    coarse with 4 s windows in half second steps, then fine with 1 s windows
    in 50 ms steps around the edge found. The coarse window finds the edge
    reliably but sits systematically late -- a window half inside the intro
    only half matches. The second pass recovers that.
    """
    HOP, rate = 5.0, 4000
    env_video = video_envelope(video, HOP, rate)
    env_audio = envelope(decode_audio(audio, rate=rate), HOP, rate)
    n_audio = sample_count(audio)
    if len(env_video) < 200 or len(env_audio) < 200:
        return 0, n_audio, {"reason": T('too short')}

    # The anchor is the middle of the picture, not of the audio: the audio can
    # be a multiple longer, and then its middle may lie entirely outside what
    # the camera recorded.
    m0, m1 = int(len(env_video) * 0.25), int(len(env_video) * 0.75)
    middle = env_video[m0:m1]
    nf = 1 << int(np.ceil(np.log2(len(env_audio) + len(middle))))
    cc = np.fft.irfft(np.fft.rfft(env_audio, nf)
                      * np.conj(np.fft.rfft(middle, nf)), nf)
    # Where the picture sits when the audio is at zero.
    shift = m0 - int(np.argmax(cc[:max(1, len(env_audio))]))

    def quality(i, W):
        j = i + shift
        if i < 0 or i + W > len(env_audio) or j < 0 or j + W > len(env_video):
            return 0.0
        a, b = env_audio[i:i + W], env_video[j:j + W]
        na, nb = np.sqrt((a ** 2).sum()), np.sqrt((b ** 2).sum())
        return float((a * b).sum() / (na * nb)) if na > 0 and nb > 0 else 0.0

    win_coarse = int(4.0 * 1000 / HOP)
    # Measure the reference level only where audio and picture both run.
    t0 = max(0, -shift)
    t1 = min(len(env_audio), len(env_video) - shift)
    means = [quality(i, win_coarse) for i in
                   range(t0 + int((t1 - t0) * 0.3),
                         max(t0 + int((t1 - t0) * 0.3) + 1,
                             t0 + int((t1 - t0) * 0.7)), win_coarse)]
    level = float(np.median(means)) if means else 0.0
    if level < 0.15:
        return 0, n_audio, {"reason":
                            T('no match in the middle either (%s)')
                            % decimal_text("%.2f" % level)}
    threshold = max(0.12, 0.5 * level)
    R = int(edge_s * 1000 / HOP)
    step_coarse = int(0.5 * 1000 / HOP)
    win_fine = int(1.0 * 1000 / HOP)
    step_fine = max(1, int(0.05 * 1000 / HOP))

    def edge(front):
        """Return where the part matching the picture begins or ends.

        Searched around the place it should sit after coarse alignment, not
        around the start and end of the file. Where the audio is a multiple of
        the picture in length, the edges lie far inside.
        """
        anchor = t0 if front else t1 - win_coarse
        coarse, run = None, 0
        steps = range(0, R, step_coarse)
        for d in steps:
            i = anchor + d if front else anchor - d
            if i < 0 or i + win_coarse > len(env_audio):
                continue
            if quality(i, win_coarse) > threshold:
                run += 1
                if run >= 2:
                    coarse = i if front else i + win_coarse
                    break
            else:
                run = 0
        if coarse is None:
            return max(0, t0) if front else min(len(env_audio), t1)
        best = coarse
        for k in range(1, int(6.0 * 1000 / HOP / step_fine)):
            i = coarse - k * step_fine if front else coarse + k * step_fine
            if quality(i if front else i - win_fine, win_fine) > threshold:
                best = i
            else:
                break
        return max(0, best) if front else min(len(env_audio), best)

    i0, i1 = edge(True), edge(False)
    if i1 <= i0:
        return 0, n_audio, {"reason": T('edges implausible')}
    return (max(0, int(i0 * HOP / 1000.0 * SR)),
            int(min(n_audio, i1 * HOP / 1000.0 * SR)),
            {"threshold": threshold, "level": level})


# What the phase way has to beat before it is believed instead of the
# plain one. Measured on 23.8.2026: on the music that sent us looking
# it came out at 28.7 against a nearest rival of 26.5, and the answer
# was right to twelve milliseconds. Not measured on enough material to
# call it a threshold -- it is a floor, and the log prints the number
# so anybody can see how close it was.
PHASE_SHARP_ENOUGH = 8.0


def align_on_moving_bands(x_video, x_audio, HOP, rate, sample_points,
                          window_s, distance_s):
    """The same way again, on the bands that carry movement.

    Returns what align_envelopes returns, or None where a curve came
    out too short to compare. The numbers in it are the ordinary ones
    -- sample points and their spread -- so the gate that judges the
    first answer judges this one by the same rule.
    """
    curve_video = band_envelope(x_video, HOP, rate)
    curve_audio = band_envelope(x_audio, HOP, rate)
    if len(curve_video) < 10 or len(curve_audio) < 10:
        return None
    return align_envelopes(curve_video, curve_audio, HOP, sample_points,
                           window_s, distance_s, warn=False)


def align_audio_to_video(audio, video, head_s, sample_points=None, window_s=20.0,
               distance_s=120.0):
    """Return a, b with audio time = a + b * video time."""
    HOP, rate = 5.0, 4000
    env_video = video_envelope(video, HOP, rate)
    x_audio = decode_audio(audio, rate=rate, ss=head_s / float(SR))
    env_audio = envelope(x_audio, HOP, rate)
    a, b, st = align_envelopes(env_video, env_audio, HOP, sample_points,
                               window_s, distance_s,
                               warn=os.path.basename(audio))
    if st.get("quality", 0.0) >= WEAK_MATCH:
        return a, b, st
    # The plain way found nothing worth having. Both files are read
    # here, once, for the second try and for the phase way under it --
    # the phase way read them itself before, so this costs no decode.
    x_video = decode_audio(video, rate=rate)
    second = align_on_moving_bands(x_video, x_audio, HOP, rate,
                                   sample_points, window_s, distance_s)
    if second is not None and fit_places_it(second[2]):
        # Sample points enough, and close enough to one line. Measured
        # over 293 pairs out of different productions not one gets that
        # far, and all 85 that belong together do.
        second[2]["from_bands"] = True
        return second
    # Both curves came up empty. The phase way -- it only ever runs
    # here, where the answer was going to be wrong anyway, and it is
    # the one way no sample point backs up.
    st["music_like"] = looks_like_music(env_audio)
    where, sharp = phase_align(x_video, x_audio, rate)
    st["phase_s"], st["phase_sharp"] = where, sharp
    if sharp >= PHASE_SHARP_ENOUGH:
        st["from_phase"] = True
        # No drift from this one: it answers where, not how fast. The
        # factor stays 1.0 and the report says the drift is unknown
        # rather than pretending it is zero.
        return where, 1.0, st
    # Both ways came up empty. The numbers still travel back, because
    # the log prints them, but they are marked for what they are: not
    # an alignment, a guess. Whoever asked has to decide what to do
    # with a file that has no place -- see cannot_be_placed.
    st["unplaceable"] = True
    return a, b, st


# How far a point may sit from the middle before it is thrown away.
# 3 is the ordinary choice for a robust fit; the floor keeps a very
# tight set of points from throwing away its own scatter. 20 ms is the
# floor because it is four times HOP -- what the envelope can resolve
# at all. It is a floor, not a measured threshold, and says so.
# Below this the global agreement between two envelopes is not worth
# calling a match. Not measured on real material yet -- it is the old
# 0.05 floor, kept, and now applied to the signed value instead of the
# size. What a good alignment looks like is measured: 0.5 to 0.9 on
# material that belongs together, 0.13 on a camera track against a
# finished mix of the same room.
WEAK_MATCH = 0.05

# The shortest stretch of shared sound and picture that a run will work
# with when the alignment could not place a single sample point in it.
# Where it did place points, the length does not matter -- what was
# measured was measured. Ten seconds because the alignment's own spacing
# is a couple of seconds and a handful of them is the least that says
# anything; the thirty that stood here before was a round number nobody
# had measured, and it refused 26 seconds of picture that come out exact.
AXIS_MIN_WINDOW_S = 10.0

# What one camera has to match another by before it is laid on the axis.
# Far above WEAK_MATCH: between two cameras there is no phase way to fall
# back on, so the envelopes are the whole measurement, and the floor for
# "nothing at all" is not the number for "these two heard the same room".
#
#   camera against camera, 21 s against 26 s      0.837   right
#   camera against camera, 68 min against 68 min  0.811   right
#   an 18-second jingle against 68 min of camera  0.210   nonsense
#
# Measured 30.8.2026; two recordings of different conversations came to
# 0.21 to 0.27 the same day. A real match sits above 0.8, unrelated
# material with structure near 0.25, and half is the middle of the gap.
CAMERA_MATCH_ENOUGH = 0.5
# Measured 1.9.2026, four productions, 85 pairs that belong together
# against 293 that do not: the correlation overlaps (worst real 0.203,
# best foreign 0.124), the fit does not (62 against 43 sample points,
# 11.3 against 22.4 ms).
FIT_POINTS_ENOUGH = 50
FIT_SPREAD_MS = 15.0


def fit_places_it(st):
    """Report whether the sample points alone place this file.

    The correlation above compares two loudness curves over the whole
    runtime, and a steady tone in one of them -- mains hum -- pushes it
    down without moving where the file belongs. The fit does move with
    the answer: many points spread over the runtime, all on one line.
    A file that fits nowhere gets neither.
    """
    spread = st.get("spread_ms")
    return (st.get("points", 0) >= FIT_POINTS_ENOUGH
            and spread is not None and spread <= FIT_SPREAD_MS)


# Against a sound recording a real match reads far lower, so this floor
# only tells a measurement from noise. It stood as a bare 0.15 in the
# middle of the axis measurement until 31.8.2026.
SOUND_MATCH_ENOUGH = 0.15
# Not the count of sample points: they are set 30 seconds apart, so
# shorter material has none at all -- the 21-second camera above had
# none and was placed exactly right.


def timecode_places_it(own, others):
    """Report whether a timecode can put this file among the others.

    A timecode alone places nothing. It is a reading of a clock, and a
    reading only says something next to a second one: the file has to
    carry one and so has something else in the material. Where a
    single file has a timecode and no other does, it is as unplaced as
    if it had none.
    """
    return own is not None and any(t is not None for t in others)


def files_with_no_place(weak, clocks):
    """Which of the badly fitting files no clock places either.

    The one reading of "it fits nowhere": the intro proposal and the
    bar on the wide shot both ask here. Weak alone is not it -- a
    camera whose sound says nothing is still placed by its timecode --
    and below the floor is not it either, because that is measured
    against nothing at all and a jingle lands above it.
    """
    return [p for p in weak
            if not timecode_places_it(
                clocks.get(p), [t for q, t in clocks.items() if q != p])]


def cannot_be_placed(st, own_tc, other_tcs):
    """Report whether an alignment left a file with no place at all.

    Two ways lead to a place, and either one is enough. The timecode
    is the first, and where it answers the sound is not asked at all:
    a camera whose microphone heard nothing of the room is still
    placed to the frame by its clock, and refusing it because of its
    sound would throw away a file that is in fact known to the
    millisecond. The measurement is the second way, and *st* carries
    its verdict: "unplaceable" stands there when every way of
    measuring came up empty.

    Only where neither answers is there nothing left. Then the file is
    refused rather than laid down somewhere, because laid down
    somewhere it looks exactly like a file that fits.

    Not by the count of sample points, though that was tried on
    30.8.2026 and reverted the same hour: on the ordinary path a
    measurement with no sample points is still a measurement -- the
    offset comes from the cross correlation and only the clock drift is
    missing, which is what "too few sample points for a drift
    measurement" says. Reading that as "no place" refused material the
    tests prove is placed to the sample.
    """
    if not (st or {}).get("unplaceable"):
        return False
    return not timecode_places_it(own_tc, other_tcs)


def which_way_placed(st, hint=""):
    """Add to a track's note which way put it on the axis.

    The plain loudness curve says nothing, being the ordinary answer;
    the two later ways do, and both report lines use this one function
    so they say the same thing. The phase carries its sharpness against
    PHASE_SHARP_ENOUGH, and says the drift is unknown: it answers where
    a track sits, not how fast it ran, and the line beside it prints
    +0.00 ppm, which would otherwise read as a drift measured at zero.
    """
    if (st or {}).get("from_bands"):
        hint = (hint + ", " if hint else "") + T('placed on the bands '
                                                 'that move')
    if (st or {}).get("from_phase"):
        hint = (hint + ", " if hint else "") + (
            T('placed by phase, sharpness %s against a floor of %s, '
              'drift unknown')
            % (decimal_text("%.1f" % float(st.get("phase_sharp") or 0.0)),
               decimal_text("%.1f" % PHASE_SHARP_ENOUGH)))
    return hint


def no_place_message(name):
    """Say that a file cannot be placed, and what would fix it."""
    return T('%s cannot be placed: its sound has nothing in common '
             'with the rest of the material, and the file carries no '
             'timecode. It needs one that fits the other recordings, '
             'and that has to be set with another program.') % name


def timecode_seconds(info):
    """The timecode in a video's facts, in seconds, or nothing."""
    if not (info or {}).get("tc"):
        return None
    try:
        return parse_timecode(info["tc"], max(1.0, info.get("fps") or 30.0))
    except (ValueError, TypeError):
        return None


OUTLIER_SIGMA = 3.0
OUTLIER_FLOOR_S = 0.020
OUTLIER_ROUNDS = 6


def _spans_share(tv, duration_v):
    """How much of the runtime the surviving points still cover.

    A set that has been cleaned down to one corner of the recording
    looks tidy and says nothing about the rest of it.
    """
    if len(tv) < 2 or duration_v <= 0:
        return 0.0
    return float((max(tv) - min(tv)) / duration_v)


def without_outliers(tv, dt):
    """Throw away points that lie far from the others. (tv, dt, dropped).

    The anchor is the median, not the line: a single outlier tips the
    line, and then the wrong points look like the odd ones out. The
    scatter is measured as the median absolute deviation, scaled by
    1.4826 so it means the same as a standard deviation on ordinary
    data.

    Six rounds at most, and never below three points -- two points
    always fit a line perfectly, which would turn a broken measurement
    into a confident one. Every point thrown away is named in the log:
    a run that cleans up in silence cannot be checked afterwards.
    """
    kept_t, kept_d = np.asarray(tv, float), np.asarray(dt, float)
    dropped = []
    for _ in range(OUTLIER_ROUNDS):
        if len(kept_t) < 4:
            break
        b, a = np.polyfit(kept_t, kept_d, 1)
        rest = kept_d - (a + b * kept_t)
        middle = float(np.median(rest))
        mad = float(np.median(np.abs(rest - middle))) * 1.4826
        limit = max(OUTLIER_SIGMA * mad, OUTLIER_FLOOR_S)
        keep = np.abs(rest - middle) <= limit
        if keep.all() or int(keep.sum()) < 3:
            break
        for i in np.flatnonzero(~keep):
            dropped.append((float(kept_t[i]), float(rest[i]) * 1000))
        kept_t, kept_d = kept_t[keep], kept_d[keep]
    return kept_t, kept_d, dropped


def align_envelopes(env_video, env_audio, HOP=5.0, sample_points=None, window_s=20.0,
                       distance_s=120.0, points_off="video", warn=True):
    """The same on ready-made envelopes.

    Which way round: the second curve's time = a + b * the first
    curve's time. Said without the word "reference" on purpose --
    align_cameras calls the *first* of its two the reference, and
    reading this line with that meaning turns the pair round.

    *points_off* decides which of the two curves the sample points are
    picked on; the first by default. For a de-bled speaker track it has to
    be the second: only one speaker is left there, and only where they speak
    is there anything to compare. Picking the spots on the camera track
    would land mostly in passages where somebody else talks.

    The number of sample points grows with the runtime -- about one every
    two minutes, at least nine. More points make the slope more certain, and
    the slope is the clock drift. The envelopes are in memory anyway, so an
    extra point costs almost nothing. Kept separate from align_audio_to_video
    so two cameras can be compared without reading the large files twice.
    """
    if len(env_video) < 10 or len(env_audio) < 10:
        raise RuntimeError(T('too little audio to align'))
    if points_off == "audio":
        a, b, st = align_envelopes(env_audio, env_video, HOP, sample_points, window_s,
                                      distance_s, warn=warn)
        return -a / b, 1.0 / b, st
    k, g = cross_correlate(env_video, env_audio)
    coarse = k * HOP / 1000.0
    # Signed, not by size: see cross_correlate. Said out loud even
    # where it passes, because "found something" and "found it barely"
    # look the same from outside. A second try on the same two files
    # has heard it once and asks for silence.
    if warn and g < WEAK_MATCH:
        # warn carries the name where the caller has one. Without it
        # a run with several recordings prints a heap of warnings
        # nobody can put back against a file.
        print(as_warn(T('      WARNING: weak match for %s (%s, %s is '
                        'the floor). The two may not belong together.')
                      % (warn if isinstance(warn, str)
                         else T('this pair of files'),
                         decimal_text("%.3f" % g),
                         decimal_text("%.2f" % WEAK_MATCH))))

    duration_v = len(env_video) * HOP / 1000.0
    W = int(window_s * 1000 / HOP)
    # Create twice as many candidates as needed -- the uninteresting ones drop
    # out immediately, and too many beats too few.
    if sample_points is None:
        sample_points = max(9, min(80, int(duration_v / distance_s) + 1))
    candidates = max(sample_points * 2, 12)
    spread_total = float(np.std(env_video)) or 1.0

    points, with_signal = [], 0
    for i in range(candidates):
        t = duration_v * (i + 0.5) / candidates
        i0 = int(t * 1000 / HOP) - W // 2
        if i0 < 0 or i0 + W > len(env_video):
            continue
        seg = env_video[i0:i0 + W]
        # Silence or steady noise is no use for comparison: there are no edges
        # to align on.
        if float(np.std(seg)) < 0.35 * spread_total:
            continue
        with_signal += 1
        j0 = i0 + int(round(coarse * 1000 / HOP))
        pad = int(2000 / HOP)
        if j0 - pad < 0 or j0 + W + pad > len(env_audio):
            continue
        around = env_audio[j0 - pad:j0 + W + pad]
        nf = 1 << int(np.ceil(np.log2(len(around) + len(seg))))
        cc = np.fft.irfft(np.fft.rfft(around, nf) * np.conj(np.fft.rfft(seg, nf)), nf)
        kk = int(np.argmax(cc[:2 * pad + 1])) - pad
        label_text = np.sqrt((seg ** 2).sum() * (around[pad + kk:pad + kk + W] ** 2).sum())
        if label_text <= 0:
            continue
        if float(cc[kk + pad] / label_text) > 0.2:
            points.append((t, coarse + kk * HOP / 1000.0))
    count_n = {"candidates": candidates, "with_signal": with_signal,
                "points": len(points)}

    if len(points) >= 3:
        tv = np.array([p[0] for p in points])
        dt = np.array([p[1] for p in points])
        # What the raw points say, before anything is thrown away. It
        # stays in the report: a run that quietly cleans itself up and
        # then calls the result good has traded a loud fault for a
        # quiet one.
        b0, a0 = np.polyfit(tv, dt, 1)
        raw_spread = float(np.std(dt - (a0 + b0 * tv)) * 1000)
        tv, dt, dropped = without_outliers(tv, dt)
        b, a = np.polyfit(tv, dt, 1)
        rest = dt - (a + b * tv)
        n = len(tv)
        sxx = float(((tv - tv.mean()) ** 2).sum())
        s2 = float((rest ** 2).sum()) / max(1, n - 2)
        se_b = (s2 / sxx) ** 0.5 if sxx > 0 else float("inf")
        count_n.update({"ppm": b * 1e6, "ppm_error": se_b * 1e6,
                         "spread_ms": float(np.std(rest) * 1000), "quality": g,
                         "raw_spread_ms": raw_spread,
                         "dropped": dropped,
                         "spans_share": _spans_share(tv, duration_v),
                         "offsets": [float(x) for x in dt],
                         "times": [float(x) for x in tv]})
        return a, 1.0 + b, count_n
    count_n["quality"] = g
    return coarse, 1.0, count_n


#--------------------------------------------- Keeping itself up to date

# =====================================================================
#  Keeping itself up to date
# =====================================================================
# The program can look whether a newer release is out and, if somebody
# says so, fetch it and start again. Three rules hold it in place:
#
#   * Looking is free and needs no permission: one question for a
#     version number, nothing sent. It always looks; only
#     VPM_NO_UPDATE_CHECK stops it, and that belongs to the machine.
#   * Fetching is asked every single time: the window in a box, the
#     command line with a line and --update. Never unasked, and never
#     while a run is going on.
#   * What comes down is read before it is used: a file that does not
#     compile is not written over the one that works.

RELEASES = ("https://api.github.com/repos/Bascht74/videopodcast-magic"
            "/releases/latest")
# The whole list, for the versions in between. Whoever skipped two
# releases wants to read all three, not only the newest.
RELEASE_LIST = ("https://api.github.com/repos/Bascht74/videopodcast-magic"
                "/releases?per_page=30")
RAW_FILE = ("https://raw.githubusercontent.com/Bascht74"
            "/videopodcast-magic/%s/videopodcast_magic/__init__.py")
# Off for a test run: a suite must not reach for the network, and it
# must certainly not swap the file it is testing.
UPDATE_OFF = bool(os.environ.get("VPM_NO_UPDATE_CHECK"))
# What pip is pointed at where the program was installed rather than
# downloaded. No PyPI in it: pip reads the repository itself and
# compares what is there with what is installed.
PIP_SOURCE = "git+https://github.com/Bascht74/videopodcast-magic"
UPDATE_SINK = None   # set by the GUI: callable(job) that runs job(say)
                     # in a thread, its lines going into the Output tab


def update_skip_file():
    """Where the version somebody chose to pass over is kept."""
    folder = cache_folder()
    return os.path.join(folder, "update_skip") if folder else ""


def update_skipped():
    """The version somebody chose to pass over, or "" for none."""
    where = update_skip_file()
    if not where or not os.path.exists(where):
        return ""
    try:
        with open(where, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def set_update_skipped(tag):
    """Pass over this one version. The next one asks again.

    In place of "do not ask again", which stopped the looking for
    good: a no that cannot be taken back is a trap, and this program
    has walked the owner into it twice. One version passed over is not
    an answer about all of them, and nothing else here says no.
    """
    where = update_skip_file()
    if not where:
        return
    try:
        with open(where, "w", encoding="utf-8") as f:
            f.write(str(tag or ""))
    except OSError:
        return


# PEP 440 hangs the pre-release straight on the numbers, with no dash:
# a1 is an alpha, b0 a beta, rc1 a release candidate. Without a number
# it means the zeroth of them, so 3.0.0b reads as 3.0.0b0.
PIP_PRE_RELEASE = re.compile(r"^(\d+(?:\.\d+)*)(a|b|rc)(\d*)$")


def pre_release_key(pre):
    """The name of a pre-release, cut so that ten comes after nine.

    Runs of digits and runs of everything else, each run of digits as
    the number it is. The 0 and the 1 in front keep the two kinds
    apart, so a number is never held against a word: b9 falls under
    b10 and beta.2 under beta.10, where either read as text would sort
    the other way round.
    """
    return tuple((0, int(run)) if run.isdigit() else (1, run)
                 for run in re.findall(r"\d+|\D+", pre))


def version_key(text):
    """A version as something that can be compared.

    Two spellings and one order: 2.0.0-beta the way the tags read, and
    3.0.0b0 the way pip writes it. Both are older than the same
    numbers with nothing hung on them, which is what Semantic
    Versioning and PEP 440 both say. Anything unreadable sorts oldest,
    so a name nobody understands never counts as newer.
    """
    text = str(text or "").strip().lstrip("vV")
    core, _, pre = text.partition("-")
    hung_on = None if pre else PIP_PRE_RELEASE.match(core)
    if hung_on:
        core = hung_on.group(1)
        pre = hung_on.group(2) + (hung_on.group(3) or "0")
    numbers = []
    for piece in core.split(".")[:3]:
        numbers.append(int(piece) if piece.isdigit() else 0)
    while len(numbers) < 3:
        numbers.append(0)
    # 1 for a finished release, 0 for a pre-release: that way 2.0.0
    # comes after 2.0.0-beta, which is what the standard says.
    return (tuple(numbers), 1 if not pre else 0, pre_release_key(pre))


def releases_in_between(newest, running):
    """The release texts from *running* up to *newest*, newest first.

    Somebody who skipped two versions was shown the newest text alone
    and had to guess at the rest. GitHub answers with the whole list,
    so the versions in between cost one more request and no thought.

    Returns "" where the list cannot be had. The caller then keeps the
    single text it already has, which is what was shown before -- a
    failure here must never be worse than not asking.
    """
    try:
        import urllib.request
        with urllib.request.urlopen(RELEASE_LIST, context=https_context(),
                                    timeout=20) as answer:
            found = json.load(answer)
    except Exception:
        return ""
    if not isinstance(found, list):
        return ""
    want = []
    for one in found:
        if not isinstance(one, dict) or one.get("draft"):
            continue
        tag = str(one.get("tag_name") or "")
        if not tag:
            continue
        # Strictly between: the newest is already in hand, and the
        # running one is what somebody has.
        if version_key(running) < version_key(tag) <= version_key(newest):
            want.append((version_key(tag), tag,
                         str(one.get("body") or "").strip()))
    want.sort(reverse=True)
    # Each one cut to the language this is running in, here rather than
    # where it is shown: two windows show this text, and only one of
    # them was cutting. The other handed a German reader the English
    # half, which is the half that comes first.
    return "\n\n".join("## %s\n\n%s" % (tag, release_text_in(body))
                        for _k, tag, body in want if body)


def newer_release(asked=False):
    """(tag, page, what changed, trouble) of a newer release.

    All four are "" where a newer release was looked for and none was
    there. *trouble* carries a sentence where the looking itself could
    not happen -- no network, or a certificate store this Python cannot
    read. That is not the same answer as "nothing newer", and it must
    not read as one: a program that says something reassuring where it
    knows nothing is worse than one that says it does not know.

    A pre-release is never the answer: GitHub only calls one release
    the latest, and it is never one put out for trying.

    The third piece is the release text itself. An address alone asks
    somebody to open a browser to find out what they are about to
    install, and most will not: they will click yes without knowing.
    It comes down with the same answer, so it costs nothing.

    *asked* is a direct question -- from the menu or from --update. A
    version passed over does not stand against that;
    VPM_NO_UPDATE_CHECK does, because that one is set by whoever runs
    the machine rather than by whoever clicks.
    """
    if UPDATE_OFF:
        return "", "", "", ""
    passed_over = "" if asked else update_skipped()
    try:
        import urllib.request
        with urllib.request.urlopen(RELEASES, context=https_context(),
                                    timeout=20) as answer:
            found = json.load(answer)
    except Exception as e:
        # Said, not swallowed. Whoever did not ask is not told -- a
        # start without a network would otherwise complain every time.
        return "", "", "", (T('Could not look for a newer version: %s')
                            % e if asked else "")
    tag = str(found.get("tag_name") or "")
    if passed_over and tag == passed_over:
        # Passed over once, so it is not offered again by itself. The
        # next release has another name and asks, and the menu asks
        # whenever somebody wants it to.
        return "", "", "", ""
    if not tag or version_key(tag) <= version_key(VERSION):
        # Nothing newer. The answer already carries the text of the
        # release that is running, and throwing it away means asking
        # somebody to open a browser to read what they already have.
        # It comes back with an empty tag, so callers that only want a
        # newer version are unaffected.
        same = version_key(tag) == version_key(VERSION) if tag else False
        return ("", str(found.get("html_url") or "") if same else "",
                str(found.get("body") or "").strip() if same else "", "")
    text = str(found.get("body") or "").strip()
    # Two versions may lie between what runs here and what is out.
    # Showing only the newest hides what somebody is also getting.
    whole = releases_in_between(tag, VERSION)
    return (tag, str(found.get("html_url") or ""), whole or text, "")


def self_checked(raw):
    """Read before it is believed: (text, "") or ("", why).

    Three questions of anything that is about to become this program:
    is it readable text, does it look like this program rather than
    like an error page a proxy put there, and does it compile. They are
    asked of what comes down from the network and of what lies beside
    the program as .old -- the second one has nothing behind it to fall
    back on, so it is asked exactly as hard.
    """
    if isinstance(raw, bytes):
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return "", T('That file is not readable text.')
    else:
        text = raw
    if "VERSION = " not in text or "CATALOGUE" not in text:
        return "", T('That file is not this program.')
    try:
        compile(text, "videopodcast_magic/__init__.py", "exec")
    except SyntaxError as e:
        return "", T('That file does not compile: line %s.') % e.lineno
    return text, ""


def fetch_new_self(tag):
    """Fetch that release of this program. (text, "") or ("", why)."""
    try:
        import urllib.request
        with urllib.request.urlopen(RAW_FILE % tag,
                                    context=https_context(),
                                    timeout=120) as answer:
            raw = answer.read()
    except Exception as e:
        return "", T('The new version could not be fetched: %s') % e
    return self_checked(raw)


def put_new_self(text):
    """Write it in place of this file, the old one kept beside it.

    Returns "" when it worked. The old file stays as .old: an update
    that turns out wrong should not need the network to be undone.

    Where a package manager owns the folder, nothing is written: that
    would leave its record of the version standing and wrong.
    """
    here = os.path.abspath(__file__)
    owner = installed_by_a_package_manager()
    if owner:
        return T('This was installed rather than downloaded, into %s. '
                 'Update it the way it was installed, or the record '
                 'kept there would go on naming the old version.') % owner
    try:
        beside = here + ".new"
        with open(beside, "w", encoding="utf-8") as f:
            f.write(text)
        shutil.copymode(here, beside)
        shutil.copyfile(here, here + ".old")
        os.replace(beside, here)
    except OSError as e:
        return T('The new version could not be written: %s') % e
    return ""


def pip_update(tag, say):
    """Let pip fetch that release. "" when it worked, or why not.

    The Python this is running in, so the installation that gets the
    new version is the one that would run it. Every line pip writes is
    handed on as it arrives: the first install fetches a gigabyte of
    packages, and a window with nothing in it looks broken.
    """
    order = [sys.executable, "-m", "pip", "install", "-U", PIP_SOURCE]
    say("  %s\n" % " ".join(order))
    try:
        started = subprocess.Popen(order, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
    except OSError as e:
        return T('pip could not be started: %s') % e
    for line in started.stdout:
        say(line.decode("utf-8", "replace"))
    code = started.wait()
    if code:
        return T('pip stopped with %s. What it managed stands in the '
                 'lines above.') % code
    say(T('%s is installed. It runs from the next start.') % tag + "\n")
    return ""


def update_promise(owner):
    """What the window says it will do before it asks.

    Two different things happen, so two different sentences are owed.
    *owner* is the folder a package manager installed this into, and
    where there is one the program does not write over itself: pip
    does it, into that folder.
    """
    if owner:
        return T('Update? pip fetches it into %s. What pip says appears '
                 'under Output, and the new version runs from the next '
                 'start.') % owner
    return T('Update? The run then begins from the new version. The one '
             'running now stays beside it as videopodcast_magic.py.old.')


def update_fetched(tag, owner):
    """Put that release in place. "" where it is under way, or why not.

    An installation is pip's to change: writing over the file would
    leave its record of the version standing and wrong. pip takes
    minutes, so the window runs it beside itself rather than in its
    own thread. A loose file is written over and the program starts
    again from it.
    """
    if owner:
        if UPDATE_SINK is None:
            return T('There is no window to show what pip says.')
        UPDATE_SINK(lambda say: pip_update(tag, say))
        return ""
    text, trouble = fetch_new_self(tag)
    if not text:
        return trouble
    trouble = put_new_self(text)
    if trouble:
        return trouble
    start_again()
    return ""


def update_note():
    """Say on the command line that a newer version is out.

    A line and nothing else. A run started out of a script must not
    stop to ask anything, so there is no box and no question here, and
    nothing at all is fetched: --update does that, and only that.
    """
    tag, page, _changed, _trouble = newer_release()
    if not tag:
        return
    print(T('%s is out. This is %s.') % (tag, VERSION))
    print(T('--update fetches it and puts it in place.'))
    if page:
        print("  %s" % page)


def update_from_command_line():
    """Fetch the newer version and put it in place. 0, or 1 with a word.

    Asked for outright, so a version passed over in the window does not
    stand against it. Nothing is started again afterwards: a command
    line hands the next run back to whoever is at the keyboard.
    """
    if UPDATE_OFF:
        print(T('The check for new versions is switched off here.'))
        return 1
    tag, _page, _changed, trouble = newer_release(asked=True)
    if trouble:
        print(trouble)
        return 1
    if not tag:
        print(T('No newer version found. This one is %s.') % VERSION)
        return 0
    if installed_by_a_package_manager():
        # Whoever typed --update has a console, so pip writes into it.
        trouble = pip_update(tag, write_through)
        if trouble:
            print(trouble)
            return 1
        return 0
    text, trouble = fetch_new_self(tag)
    if not text:
        print(trouble)
        return 1
    trouble = put_new_self(text)
    if trouble:
        print(trouble)
        return 1
    print(T('%s is in place. The version before it is beside it as '
            'videopodcast_magic.py.old.') % tag)
    return 0


def old_self_file():
    """The version kept beside this one by an update, or "".

    Only when it is really there. The way back is not offered greyed
    out where there is nothing to go back to -- a switch that can never
    be pressed is a question nobody answers.
    """
    beside = os.path.abspath(__file__) + ".old"
    return beside if os.path.isfile(beside) else ""


def version_in_file(path):
    """The version a copy of this program carries, or "".

    Read out of the text, not by importing it: importing a file that
    may be broken is the very thing the caller is trying to avoid.
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return ""
    found = re.search(r'^VERSION = "([^"]+)"', text, re.M)
    return found.group(1) if found else ""


def restore_old_self():
    """Put the kept version back in place of this one. "" or why not.

    The kept file is used up: afterwards it is the program and there is
    no .old any more, so the entry offering this disappears by itself.
    The way forward is the update over the network again, one file of
    about a megabyte.

    Nothing is touched unless the kept file passes the same three
    checks an update passes. It is the only guard there is here.
    """
    beside = old_self_file()
    if not beside:
        return T('There is no version kept beside this one.')
    try:
        with open(beside, "rb") as f:
            raw = f.read()
    except OSError as e:
        return T('The kept version could not be read: %s') % e
    text, trouble = self_checked(raw)
    if trouble:
        return trouble
    here = os.path.abspath(__file__)
    step = here + ".back"
    try:
        with open(step, "w", encoding="utf-8") as f:
            f.write(text)
        shutil.copymode(here, step)
        # Written beside it and then moved over in one go: a program
        # file caught half written is one that starts no more.
        os.replace(step, here)
    except OSError as e:
        return T('The kept version could not be put in place: %s') % e
    try:
        os.remove(beside)
    except OSError as e:
        # The swap has happened, so this is not a failure -- but the
        # leftover copy keeps the menu entry standing, and it now holds
        # what is already running. Offering it again would do nothing,
        # and somebody would wonder why. So it says so once.
        print(T('The kept copy could not be removed: %s\n  It holds '
                'what is running now. %s can go.') % (e, beside))
    return ""


def start_again():
    """Start this program once more, in place of this run."""
    here = os.path.abspath(__file__)
    try:
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, here] + sys.argv[1:])
    except OSError as e:
        print(T('Starting again did not work: %s') % e)
        print(T('Start it by hand: %s %s') % (sys.executable, here))


#---------------------------------------------------------- Certificates

def use_certificates():
    """Point the libraries that fetch on their own at the bundle.

    They read these two variables and nothing else; without them the
    model download fails on a Python that has no certificates.
    """
    bundle = certificate_file()
    if not bundle:
        print(T('  No certificate bundle found -- an HTTPS download '
                'may fail.'))
        return None
    os.environ.setdefault("SSL_CERT_FILE", bundle)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", bundle)
    return bundle


#---------------------------------------------------------- What is said
# A piece of its own, in the folder "speech" beside this one. Read
# here and not where it is first used, because it binds what it takes
# out of this file: use_certificates above is the last of that.

speech = beside("speech", program=PROGRAM)
take_from(speech)

# What this file itself calls out of the recognition. The rest of what
# it brings answers here too, through take_from above; these are
# written out because they are read in this file, and a name read here
# and bound nowhere here is a loose end.
CLOSING_MARKS = speech.CLOSING_MARKS
clause_break_times = speech.clause_break_times
recognise_speech = speech.recognise_speech
sentence_start_times = speech.sentence_start_times
sentences_of = speech.sentences_of
speech_word = speech.speech_word
speech_words_kick_off = speech.speech_words_kick_off
words_for_handover = speech.words_for_handover
words_from_handover = speech.words_from_handover
words_of_recording = speech.words_of_recording
write_transcript_files = speech.write_transcript_files


#---------------------------------------------------------------- Building

# =====================================================================
#  Preflight
#  ---------
#  Before the first long step begins: does the material fit together?
#  A two hour run that fails at the end over a detail is more
#  expensive than a minute of checking -- and a production uploaded to
#  auphonic.com with the wrong settings costs credit on top.
#
#  The report is the same for both modes and is called from one place,
#  before the fork. What needs several tracks -- the crosstalk -- simply
#  falls away with one track.
# =====================================================================

# How much separation the 3:1 rule asks for: with the other microphone three
# times as far away as the speaker's own, the neighbouring voice is about 9.5
# dB quieter -- 20*log10(3). Below that, crosstalk starts to be audible in the
# mix as a comb filter.
THREE_TO_ONE_DB = 9.5

# The kind of a video file in the project. Content is a camera like any
# other; intro and outro are finished clips that are neither aligned nor
# processed -- they only go into the timeline.


class Finding(object):
    """One item from the preflight report.

    Four kinds, and the kind decides what happens next: "good" is only
    counted, "hint" appears in the report, "fixed" says the script
    fixed it itself, and "abort" stops the run unless --anyway is
    given.
    """

    def __init__(self, kind, field, text, advice="", file=""):
        self.kind = kind
        self.field = field
        self.text = text
        self.advice = advice
        # Which file the finding belongs to. Empty means it only arises from
        # comparing several files. The interface hangs the mark on it; a name
        # comparison would be too imprecise here.
        self.file = file
        # Belongs to a file that does not take part. It is checked anyway -- a
        # row without a mark looks forgotten -- but its finding does not count
        # towards the balance and holds nothing up.
        self.set_aside = False

    def line(self, width=17):
        label = {"good": "", "hint": T('Note: '), "fixed": T('fixed: '),
                 "abort": T('Caution: ')}[self.kind]
        out = "    %-*s %s%s" % (width, self.field, label, self.text)
        return as_warn(out) if self.kind == "abort" else out


# What a cached measurement contains changes with the script. This number is
# part of the fingerprint: raising it makes all old measurements stale and they
# are taken once more. Without it the interface would show the old result for
# weeks after an extension.
#   2  the recording curve from the logs atom was added
MEASUREMENT_VERSION = 2


def _fingerprint(paths):
    """Return a fingerprint: version, language, path, size and mtime.

    A changed file gets a different fingerprint and is measured again.
    Unchanged, the earlier measurement stands.

    The language belongs in it because a stored finding holds its text
    ready-made. Without it a run in one language would serve the report of
    the last run in the other.
    """
    if isinstance(paths, str):
        paths = [paths]
    parts = ["format %d %s" % (MEASUREMENT_VERSION, LANG)]
    for x in sorted(paths):
        try:
            s = os.stat(x)
            parts.append("%s|%d|%d" % (os.path.abspath(x), s.st_size,
                                       int(s.st_mtime)))
        except OSError:
            parts.append("%s|?" % os.path.abspath(x))
    import hashlib
    return hashlib.sha1("\n".join(parts).encode("utf-8")).hexdigest()[:16]


def cache_path(fingerprint):
    """Return where a cached measurement lives, or None."""
    folder = cache_folder("preflight")
    return os.path.join(folder, fingerprint + ".json") if folder else None


def cache_read(fingerprint):
    """Read a cached measurement. None means: measure again."""
    file_path = cache_path(fingerprint)
    if not file_path or not os.path.exists(file_path):
        return None
    try:
        with open(file_path, encoding="utf-8") as f:
            d = json.load(f)
    except (ValueError, OSError):
        return None
    if d.get("version") != VERSION:
        return None            # a new version may check differently
    return d




def cache_write(fingerprint, content):
    """Store a measurement so the next run need not repeat it."""
    d = dict(content)
    d["version"] = VERSION
    d.setdefault("when", time.time())
    write_beside_then_move(
        cache_path(fingerprint),
        json.dumps(d, ensure_ascii=False).encode("utf-8"))


def clean_preflight_cache(days=30):
    """Discard stale measurements; once per run is enough.

    Every entry names the version that wrote it and is refused after an
    update, so without this the folder keeps a dead layer for every
    release it has lived through.
    """
    clean_old_files(cache_folder("preflight"), days)


def _findings_to_json(findings):
    return [{"kind": b.kind, "field": b.field, "text": b.text, "advice": b.advice,
             "file": b.file} for b in findings]


def _findings_from_json(raw):
    return [Finding(b["kind"], b["field"], b["text"], b.get("advice", ""),
                   b.get("file", "")) for b in (raw or [])]


def measure_cached(file_path, label, measure, fresh=False):
    """Measure *one* file, from the cache or freshly.

    Cached per file, not per selection: in the interface files arrive one
    after another, and adding the fifth should not wait for the first four
    to be measured. Returns {"findings": [...], "data": {...}}; the data
    feeds the comparison across all files.
    """
    fingerprint = "%s_%s" % (label, _fingerprint(file_path))
    d = None if fresh else cache_read(fingerprint)
    if d is None:
        try:
            findings, data = measure(file_path)
        except Exception as e:
            findings = [Finding("hint", os.path.basename(file_path)[:24],
                              T('not readable: %s') % str(e)[:80])]
            data = {}
        d = {"findings": _findings_to_json(findings), "data": data}
        cache_write(fingerprint, d)
    findings = _findings_from_json(d.get("findings"))
    for b in findings:
        b.file = os.path.abspath(file_path)
    return findings, (d.get("data") or {})


def sample_frame_intervals(file_path, duration, spots=5, window_s=2.0):
    """Sample the intervals between frames at several points in the file.

    Returns one list of intervals in seconds per point. The *packets* are
    queried, not the frames: a packet is a frame, its timestamp is in the
    container, and ffprobe decodes nothing for it. On a 4K file that is the
    difference between a blink and half a minute.

    Read in time windows rather than packet counts: ffprobe always resumes
    at the keyframe before a seek, and with long groups of pictures a window
    of 48 packets would still lie entirely before the intended spot. Without
    this sample only the average would be known, and that looks the same for
    a variable rate as for a fixed one.
    """
    if not duration or duration <= 0:
        points = [0.0]
    else:
        points = [duration * k / float(spots) for k in range(spots)]
    # All the points in one call. ffprobe takes a comma separated list of
    # intervals, and every call is a process: five per file cost nothing
    # here and 1.8 seconds each on the Windows builder, where starting a
    # process is the expensive part. Measured 30.8.2026: this test made
    # 62 of them and took two seconds on this Mac and 126 on the builder.
    reading = ",".join("%.3f%%+%.1f" % (t0, window_s) for t0 in points)
    try:
        p = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "packet=pts_time", "-of", "csv=p=0",
             "-read_intervals", reading, file_path],
            capture_output=True, timeout=60)
    except Exception:
        return []
    times = []
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        line = line.strip().rstrip(",")
        if not line or line == "N/A":
            continue
        try:
            times.append(float(line))
        except ValueError:
            pass
    # Packets arrive in decoding order, and with H.264 B-frames that is not
    # display order: the timestamps then jump back and forth. Sort first,
    # or one measures the codec's picture structure and takes it for a
    # variable frame rate.
    #
    # Sorting also puts the windows back in order, since they do not
    # overlap: what separates them is a gap of seconds, and the same
    # test that throws away an interval too long to be one frame is what
    # cuts one window from the next.
    times.sort()
    out, window = [], []
    for a, b in zip(times, times[1:]):
        step = b - a
        if 0 < step < 0.25:
            window.append(step)
            continue
        if len(window) >= 8:
            out.append(window)
        window = []
    if len(window) >= 8:
        out.append(window)
    return out


def _rate_is_variable(window):
    """Report whether the frame timing varies, and how strongly.

    Two questions, because a single doubled interval means nothing. The
    sample cuts into the middle of a group of pictures; a frame is then
    missing at the edge and the interval beside it is exactly twice as
    large. That is an artefact of sampling, not a variable rate.

    Counted as variable only:
      * a noticeable share of odd intervals -- ones that are not a whole
        multiple of the frame duration, or
      * different frame durations at different points in the file.
    """
    if not window:
        return False, 0.0
    middles = []
    odd = total = 0
    for intervals in window:
        middle = sorted(intervals)[len(intervals) // 2]
        if middle <= 0:
            continue
        middles.append(middle)
        for d in intervals:
            multiple = d / middle
            if abs(multiple - round(multiple)) > 0.1:
                odd += 1
            total += 1
    if not middles or not total:
        return False, 0.0
    odd_share = odd / float(total)
    # Where the frame duration wanders over the file, the rate is variable,
    # even if every single interval looks clean on its own.
    drift = (max(middles) - min(middles)) / min(middles) if len(middles) > 1\
        else 0.0
    return (odd_share > 0.05 or drift > 0.02,
            max(odd_share, drift))


def inspect_frame_rate(file_path):
    """Report whether the frame rate is fixed or variable, and what it costs.

    Two questions, two routes. *Whether* the intervals between frames vary
    is what the sample shows. *How far* the file is off over its whole
    length is in the container: frame count against duration.

    The distinction matters because it decides whether anything needs doing
    at all. An even deviation -- the file says 30, it is constantly 29.98 --
    is the same as clock drift in the audio and is compensated during
    alignment. Only *uneven* frame timing cannot be caught that way: pulling
    the audio onto the average fits at the start and the end, not in the
    middle.
    """
    d = ffprobe_json(file_path)
    v = next((s for s in d.get("streams", [])
              if s.get("codec_type") == "video"), None)
    if v is None:
        return None

    def rate(field):
        try:
            num, the_one = (float(x) for x in str(v.get(field) or "0/0").split("/"))
            return num / the_one if the_one else 0.0
        except Exception:
            return 0.0

    label_text = rate("r_frame_rate") or rate("avg_frame_rate")
    duration = float(d.get("format", {}).get("duration")
                  or v.get("duration") or 0.0)
    try:
        videos = int(v.get("nb_frames") or 0)
    except ValueError:
        videos = 0
    mean = (videos / duration) if (videos and duration) else rate("avg_frame_rate")
    window = sample_frame_intervals(file_path, duration)
    varies, spread = _rate_is_variable(window)
    # How far does the file drift by the end when a program plays it at the
    # nominal rate?
    offset = (duration - videos / label_text) if (videos and label_text) else 0.0
    return {"path": file_path, "nominal": label_text, "mean": mean, "duration": duration,
            "videos": videos, "varies": varies, "spread": spread,
            "offset_s": offset, "codec": v.get("codec_name"),
            "width": v.get("width"), "height": v.get("height"),
            "gaps": sum(len(x) for x in window)}


def check_camera_file(file_path):
    """Report what the preflight has to say about *one* camera.

    Returns (findings, data). The data is what the comparison across all
    cameras needs, so no file has to be touched a second time for it.
    """
    name = os.path.basename(file_path)
    b = inspect_frame_rate(file_path)
    if not b:
        return [Finding("hint", name[:24], T('no video track'))], {}
    out = [Finding("good", name[:24], T('%s fps -- %s, %dx%d, %s frames in %s')
                   % (decimal_text("%.3f" % b["nominal"]),
                      b["codec"] or "?", b["width"] or 0, b["height"] or 0,
                      group_text(b["videos"]),
                      as_hms(b["duration"])))]
    # From when is it worth mentioning? The difference between frame count
    # times nominal rate and the track duration is a few frames on every camera
    # and has no consequences -- alignment measures against the camera audio,
    # not against this number. A whole second is a statement.
    noticeable = abs(b["offset_s"]) > 1.0
    if b["varies"]:
        out.append(Finding(
            "hint", "",
            T('Frame spacing varies by %s %% -- the frame timing is uneven.')
            % decimal_text("%.0f" % (100 * b["spread"])),
            T('Uneven frame timing cannot be evened out through the '
              'audio. If the sample points spread during alignment as '
              'well, convert to a fixed frame rate.')))
    elif noticeable:
        # Which way round it runs decides both sentences. Taken as an
        # amount, a file that runs slower than its label reads as one
        # that runs faster, and then both halves say the opposite.
        quicker = b["offset_s"] < 0
        spare = abs(b["offset_s"]) * b["nominal"]
        out.append(Finding(
            "hint", "",
            (T('%s fps, not the %s in the file -- %s more frames in '
               'the same length.') if quicker else
             T('%s fps, not the %s in the file -- %s fewer frames in '
               'the same length.'))
            % (decimal_text("%.4f" % b["mean"]),
               decimal_text("%.3f" % b["nominal"]),
               decimal_text("%.0f" % spare)),
            (T('The frames stand a little shorter; the file is not any '
               'longer for it. Editing software leaves out about one '
               'frame every %s s, and picture and camera audio stay '
               'together.') if quicker else
             T('The frames stand a little longer; the file is not any '
               'shorter for it. Editing software repeats about one '
               'frame every %s s, and picture and camera audio stay '
               'together.'))
            % decimal_text("%.0f" % (b["duration"] / max(1.0, spare)))))
    return out, {"name": name, "nominal": b["nominal"], "mean": b["mean"],
                  "duration": b["duration"], "width": b["width"],
                  "height": b["height"], "path": os.path.abspath(file_path),
                  "tc": file_timecode(file_path), "colour": list(mov_colour_tags(file_path) or ()),
                  "logs": log_curve_from_atom(_logs_atom_text(file_path))}


def compare_cameras(data):
    """What only shows when several cameras are compared."""
    out = []
    different = sorted({round(d["nominal"], 3) for d in data if d.get("nominal")})
    if len(different) > 1:
        out.append(Finding(
            "hint", T('Frame rates'),
            T('the video files run at different rates: %s')
            % ", ".join(decimal_text("%.3f" % r) for r in different),
            T('The Timeline gets one fixed rate -- the highest of them, '
              'or the next rate Resolve has above it. It converts the '
              'others; with 23.976 against 24 that is where its audio '
              'analysis tends to stall.')))
    # With Apple the recording curve is not in the colr box but in the logs
    # atom. Where that is present there is nothing to guess and nothing to
    # report -- it is read out and carried along byte for byte.
    curves = {}
    for d in data:
        if d.get("logs"):
            curves.setdefault(d["logs"], []).append(d.get("name") or "?")
    # Curve and primaries unset: say it once for all rather than per file -- it
    # is a property of the camera, not of the recording.
    without_colour = [d for d in data
                  if not d.get("logs")
                  and len(d.get("colour") or ()) >= 2
                  and d["colour"][0] == 2 and d["colour"][1] == 2]
    if without_colour:
        matrix = {d["colour"][2] for d in without_colour if len(d["colour"]) > 2}
        out.append(Finding(
            "hint", T('Colour space'),
            T('%s of %s video files carry no curve and no colour space in '
              'the colr box%s -- probably log material.')
            % (group_text(len(without_colour)), group_text(len(data)),
               T(' -- only the matrix says BT.2020')
               if matrix == {MATRIX_BT2020} else ""),
            T('Used as it stands -- nothing is invented. Check in Resolve '
              'under Clip Attributes, tab Color Space: if it says '
              '"Project" there, the input colour space was not recognised '
              'and has to be set by hand.')))
    # Differing recording curves would be worth a message; the same one
    # everywhere is not, since it is already in the colour line of every file.
    if len(curves) > 1:
        out.append(Finding(
            "hint", T('Capture curve'),
            T('the video files carry different recording curves: %s')
            # One per line: the names of three cameras behind one
            # another ran past the end of the column, and what was cut
            # off was the file name the reader needed.
            % "\n      ".join(T('%s in %s') % (k, ", ".join(v))
                              for k, v in sorted(curves.items())),
            T('It is in the logs atom of the picture description -- that '
              'is how Resolve recognises the input colour space. Different '
              'curves mean different input colour spaces.')))
    # Differently tagged cameras need different input colour spaces in Resolve.
    # That otherwise only shows once one camera looks unlike the other. Where
    # the logs atom says the same for all, the case is closed; Resolve goes by
    # that.
    tags = {}
    for d in data:
        f = d.get("colour") or ()
        if len(f) >= 3:
            tags.setdefault("%d/%d/%d" % tuple(f[:3]),
                                 []).append(d.get("name") or "?")
    every_having_curve = (len(curves) == 1
                      and sum(len(v) for v in curves.values()) == len(data))
    if len(tags) > 1 and not every_having_curve:
        out.append(Finding(
            "hint", T('Colour tag'),
            T('the video files are tagged differently: %s')
            # One tag per line, as with the curves above: "2/2/9 in
            # <camera>; 2/2/1 in <camera>" was cut off inside the first
            # camera's name.
            % "\n      ".join(T('%s in %s') % (k, ", ".join(v))
                              for k, v in sorted(tags.items())),
            T('The three numbers are primaries, curve and matrix. '
              'Different tags need different input colour spaces in '
              'Resolve -- otherwise one camera looks unlike the other.')))
    sizes = sorted({(d.get("width"), d.get("height")) for d in data
                       if d.get("width")})
    if len(sizes) > 1:
        out.append(Finding(
            "hint", T('Resolutions'),
            T('the video files have different picture sizes: %s')
            % ", ".join("%dx%d" % g for g in sizes),
            T('Resolve scales to the Timeline resolution. Anything smaller '
              'is scaled up and gets softer.')))
    return out


def find_camera_gaps(video_paths):
    """Find cameras that stopped in between.

    A camera splitting its recording into numbered blocks means they belong
    together -- but only if the next block starts where the previous one
    ends. A gap means the camera stopped, and then a piece of picture is
    missing exactly where the audio keeps running.
    """
    groups = {}
    for p in video_paths:
        name, _ = os.path.splitext(os.path.basename(p))
        m = TRAILING_NUMBER.match(name)
        if not m:
            continue
        groups.setdefault(m.group(1), []).append((int(m.group(2)), p))
    out = []
    for stem, parts in sorted(groups.items()):
        if len(parts) < 2:
            continue
        parts.sort()
        for (n1, p1), (n2, p2) in zip(parts, parts[1:]):
            t1, t2 = file_timecode(p1), file_timecode(p2)
            if t1 is None or t2 is None:
                out.append(Finding(
                    "hint", stem[:17],
                    T('multi-part, no timecode -- gaps in between cannot '
                      'be detected.'), "",
                    os.path.abspath(p2)))
                break
            try:
                d1 = float(ffprobe_json(p1).get("format", {}).get("duration") or 0.0)
            except Exception:
                d1 = 0.0
            gap = unwrap_day(t2, t1 + d1) - (t1 + d1)
            if gap > 0.5:
                out.append(Finding(
                    "hint", stem[:17],
                    T('Gap of %s between block %d and %d -- the camera '
                      'stopped.') % (as_hms(gap), n1, n2),
                    T('The cut has no picture there. When the Timeline is '
                      'built the spot stays empty, the audio runs on.'),
                    os.path.abspath(p2)))
    return out


def check_audio_file(file_path):
    """Report sample rate, bit depth, channels and length of one recording."""
    name = os.path.basename(file_path)
    d = ffprobe_json(file_path)
    a = next((s for s in d.get("streams", [])
              if s.get("codec_type") == "audio"), {})
    rate = int(a.get("sample_rate") or 0)
    channels = int(a.get("channels") or 0)
    depth = a.get("bits_per_raw_sample") or a.get("bits_per_sample") or "?"
    if str(a.get("sample_fmt", "")).startswith("flt"):
        depth = "32f"
    duration = float(d.get("format", {}).get("duration") or 0.0)
    out = [Finding("good", name[:24], "%s Hz, %s bit, %s, %s"
                   % (group_text(rate), depth,
                      channel_text(channels),
                      as_hms(duration)))]
    if rate and rate != SR:
        out.append(Finding(
            "fixed", "",
            T('%s Hz instead of %s Hz -- converted during processing.')
            % (group_text(rate), group_text(SR))))
    if channels > 2:
        out.append(Finding(
            "good", "",
            T('%s channels -- cut into tracks, see the rows above.')
            % group_text(channels),
            T('Every pair of channels is judged on its own: one stereo '
              'track, or two microphones and therefore two tracks. Silent '
              'inputs drop out. The rows under the file say what was '
              'measured, and the tick overrules it.')))
    # Clipping is invisible here otherwise, and actively so: the master
    # is measured as a sum and a limiter pulls it under -1 dBTP, so a
    # lapel microphone that was against the stop all evening comes out
    # looking clean. A hint, never a stop -- an overdriven recording is
    # sometimes the only recording there is.
    for channel, facts_ in sorted(clipping_facts(file_path).items()):
        runs, longest, milliseconds, first = facts_
        out.append(Finding(
            "hint", "",
            T('Channel %d is against the stop: %s times three samples or '
              'more in a row, the longest %s (%s ms), the first at %s.')
            % (channel + 1, group_text(runs), group_text(longest),
               decimal_text("%.1f" % milliseconds), as_hms(first)),
            T('Counted here, sample by sample, at the rate the file was '
              'recorded at: a run of three or more samples on the highest '
              'value an integer format can hold. One or two are rounding '
              'and are not reported. What is cut off there is gone and no '
              'processing brings it back -- but the recording is still the '
              'recording, and this holds nothing up. Only integer formats '
              'are counted. 32 bit float has no stop at full scale, so '
              'there is nothing there to count.'),
            os.path.abspath(file_path)))
    return out, {"name": name, "duration": duration, "rate": rate,
                  "channel_count": channels, "path": os.path.abspath(file_path),
                  "tc": file_timecode(file_path)}


def by_recording(audio_data, chains):
    """Turn per-block data into per-recording data.

    A block is not a recording: several blocks in a row make one long
    recording. Recordings are compared, otherwise every block would count
    as too short.
    """
    after_file_path = ByFile((d.get("path"), d)
                            for d in audio_data if d.get("path"))
    out = []
    for row, _rest in chains:
        parts = [after_file_path[x] for x in row
                 if x in after_file_path]
        if not parts:
            continue
        head = dict(parts[0])
        head["duration"] = sum(t.get("duration") or 0.0 for t in parts)
        if len(parts) > 1:
            head["name"] = "%s +%d" % (head.get("name") or "?",
                                       len(parts) - 1)
        out.append(head)
    return out


def compare_audio_tracks(data):
    """Find tracks that stand out against the others."""
    lengths = [(d.get("name") or "?", d.get("duration") or 0.0,
                d.get("path") or "") for d in data]
    if len(lengths) < 2:
        return []
    longer = max(d for _, d, _p in lengths)
    out = []
    for name, d, file_path in lengths:
        if longer > 0 and d < 0.5 * longer:
            out.append(Finding(
                "hint", name[:17],
                T('only %s long, the longest recording has %s.')
                % (as_hms(d), as_hms(longer)),
                T('Started late or stopped early -- this voice is then '
                  'missing from the mix in places.'), file_path))
    return out


def timecode_comparison(data):
    """Find files whose timecode belongs to an entirely different time.

    Material from one recording runs simultaneously, so the timecode windows
    overlap. A file overlapping with none of the others had an unset clock --
    typical for a recorder starting at 00:00:00 while the cameras write time
    of day.

    The rule itself is clocks_apart, and only there: what is decided
    here also decides the zero point of the cut, so the two must not
    be able to disagree about the same clock.
    """
    rows = [d for d in data if d.get("tc") is not None]
    apart, moved, placed = clocks_apart(
        [(d["tc"], max(1.0, d.get("duration") or 0.0), i)
         for i, d in enumerate(rows)])
    out = []
    if moved:
        out.append(Finding(
            "hint", T('Midnight'),
            T('%s carries a timecode from the other side of midnight -- '
              'counted as one night, not as a day apart.')
            % ", ".join(sorted(rows[i].get("name") or "?"
                               for i in moved)[:3]),
            T('A timecode counts from midnight and starts over there. '
              'The files are put on one axis before anything is '
              'subtracted, otherwise the recording after midnight looks '
              'almost a day away from the one before. If these really '
              'were recorded on different days, the alignment is wrong '
              'and the measured offset is the one to trust.')))
    for a0, _n, i in placed:
        if i not in apart:
            continue
        # Each value goes back into a timecode at the rate of the file it
        # came off. A camera running at 25 counts 25 frames to the second,
        # and printing its timecode at 30 would move it by two frames.
        other = sorted((b0, j) for b0, _m, j in placed if j != i)
        middle, other_row = other[len(other) // 2]
        out.append(Finding(
            "hint", (rows[i].get("name") or "?")[:17],
            T('Timecode %s, the other files are at %s -- this clock was '
              'not set.')
            % (timecode_string(a0, rows[i].get("nominal") or 30.0),
               timecode_string(middle, rows[other_row].get("nominal") or 30.0)),
            T('Alignment goes by the measured offset; the timecode is only '
              'the cross-check.'), rows[i].get("path") or ""))
    return out


# How far into a recording the bleed windows may reach before it is
# cheaper to read the whole thing once than to seek into it five times.
# Five minutes at 16 kHz mono is 19 MB; a two-hour interview would be
# 460, which is the reason the sampling exists at all. What this buys is
# process starts, and those are what a Windows builder charges for:
# local_run made 62 of them and took two seconds here and 126 there.
WHOLE_READ_S = 300.0


def crosstalk_apart(audio_paths, rate=16000, window=5, long=20.0,
                    min_len_long=4.0):
    """Measure how loudly each voice appears in the others' microphones.

    Not the whole recording -- too slow for a preflight -- but a few
    windows over the shared time, enough for a level ratio. Returns
    ([(who, in whose microphone, dB), ...], indices into *audio_paths*,
    plus why not. One measurement, two readers: the preflight makes
    sentences of it, the separation asks whether the tracks still tell.
    """
    if len(audio_paths) < 2:
        return [], ""
    starts = [file_timecode(p) for p in audio_paths]
    takes = []
    for p in audio_paths:
        try:
            takes.append(float(ffprobe_json(p).get("format", {})
                                .get("duration") or 0.0))
        except Exception:
            takes.append(0.0)
    if all(s is not None for s in starts):
        # Shared absolute time: measure only where all of them run.
        t0 = max(starts)
        t1 = min(s + d for s, d in zip(starts, takes))
        # With short material use smaller windows rather than giving up.
        long = max(min_len_long, min(long, (t1 - t0) / (window + 1.0)))
        if t1 - t0 < 2 * long:
            return [], T('the recordings overlap only %s -- too little '
                         'to measure.') % as_hms(max(0.0, t1 - t0))
        points = [t0 + (t1 - t0 - long) * k / float(max(1, window - 1))
                  for k in range(window)]
        offset = [[p - s for s in starts] for p in points]
    else:
        shortest = min(d for d in takes if d) if any(takes) else 0.0
        long = max(min_len_long, min(long, shortest / (window + 1.0)))
        if shortest < 2 * long:
            return [], T('the shortest recording has only %s -- too '
                         'little to measure.') % as_hms(shortest)
        points = [(shortest - long) * k / float(max(1, window - 1))
                  for k in range(window)]
        offset = [[p] * len(audio_paths) for p in points]
    data = []
    for i, p in enumerate(audio_paths):
        pieces = []
        # Five windows of 5.7 seconds out of a 34-second recording is the
        # whole file read in five processes, and the pieces are joined
        # again on the next line anyway. Where the windows reach no
        # further than a few minutes in, it is read once and cut up
        # here. Not for a two-hour interview: at this rate the whole of
        # one is 460 MB, which is what the sampling is for.
        reach = max(max(0.0, row[i]) for row in offset) + long
        if reach <= WHOLE_READ_S:
            try:
                whole = decode_audio(p, rate=rate)
                for row in offset:
                    at = int(max(0.0, row[i]) * rate)
                    piece = whole[at:at + int(long * rate)]
                    if len(piece):
                        pieces.append(piece)
            except Exception:
                pieces = []
        for row in (offset if not pieces else ()):
            try:
                pieces.append(decode_audio(p, rate=rate, ss=max(0.0, row[i]),
                                          duration=long))
            except Exception:
                pass
        if not pieces:
            return [], T('not measurable.')
        data.append(np.concatenate(pieces))
    short = min(len(x) for x in data)
    data = [np.asarray(x[:short], dtype=np.float64) for x in data]
    level, speech = _block_levels(data, rate)
    rows = []
    for i in range(len(data)):
        for j in range(len(data)):
            if i == j:
                continue
            blocks = _windows_for_pair(level, speech, i, j, at_most=30)
            if len(blocks) < 3:
                continue
            own_flag = float(np.median([level[i][b] for b in blocks]))
            others = float(np.median([level[j][b] for b in blocks]))
            if own_flag <= 0 or others <= 0:
                continue
            rows.append((i, j, 20.0 * math.log10(own_flag / others)))
    return rows, ""


def microphones_apart_db(audio_paths):
    """How far the closest pair of these microphones stands apart, in dB.

    The worst of every recording against every other, both ways round;
    None where it could not be measured. That is the number the
    separation asks before it decides whether the tracks can still say
    who is speaking on their own.
    """
    try:
        rows, _why = crosstalk_apart(audio_paths)
    except Exception:
        return None
    return min((db for _i, _j, db in rows), default=None)


def check_crosstalk(audio_paths, rate=16000, window=5, long=20.0,
                    min_len_long=4.0):
    """Say in words how much of each voice sits in the other microphones.

    The yardstick is the 3:1 rule of audio recording: with the other
    microphone three times as far from the speaker as their own, the
    neighbouring voice is about 9.5 dB quieter. That is a statement
    about the *setup in the room*, not about post-production; it can
    only be changed next time.
    """
    if len(audio_paths) < 2:
        return []
    rows, why = crosstalk_apart(audio_paths, rate, window, long,
                                min_len_long)
    if why:
        return [Finding("hint", T('Bleed'), why)]
    names = [os.path.splitext(os.path.basename(p))[0][:28] for p in audio_paths]
    out, bad = [], 0
    for i, j, separation in rows:
        good = separation >= THREE_TO_ONE_DB
        if not good:
            bad += 1
        out.append(Finding(
            "good" if good else "hint", T('Bleed'),
            T("%s%s in %s's microphone only %s dB quieter")
            % ("" if good else T('Limits the de-bleed: '),
               names[i], names[j], decimal_text("%.1f" % separation))
            if not good else
            T("%s in %s's microphone: %s dB quieter than in their own.")
            % (names[i], names[j], decimal_text("%.1f" % separation)),
            "" if good else
            T('It arose during the recording and cannot be changed '
              'now. The less the microphones are separated, the more '
              'cautiously De-Bleed at auphonic.com can work. Next '
              'time: three times as far from the neighbouring '
              'microphone as from your own mouth, then the '
              'neighbouring voice sits about %s dB lower.')
            % decimal_text("%.1f" % THREE_TO_ONE_DB),
            os.path.abspath(audio_paths[j])))
    if not out:
        return [Finding("hint", T('Bleed'),
                       T('no place found where exactly one person speaks '
                         '-- the separation cannot be measured.'))]
    if bad:
        out.append(Finding(
            "hint", T('3:1 rule'),
            T('%s of %s comparisons are below %s dB -- every recording '
              'against every other, in both directions.')
            % (group_text(bad), group_text(len(out)),
               decimal_text("%.1f" % THREE_TO_ONE_DB)),
            T('This comes from the recording, not afterwards: the '
              'microphones sit too close together or too far from the '
              'mouth.')))
    return out


# What the room has to be over the estimate before the run is called
# safe. The estimate is a rough one and says so, and a rough estimate
# passed by one per cent is not a pass: a real run cleared the old check
# by 1.1 GB of 96.6 and died at 88 per cent.
SPACE_MARGIN = 1.15


def on_one_disk(one, other):
    """Whether two folders live on the same disk.

    Unknown counts as no: a wrong yes would double an estimate that is
    already erring upward, and refuse a run that would have fitted.
    """
    try:
        return os.stat(one).st_dev == os.stat(other).st_dev
    except Exception:
        return False


def window_between(in_point, out_point, fps=30.0):
    """How long the delivered cameras are, out of In point and Out point.

    Only where both are given and count the same way is the length known
    before the axis has been measured. One point alone leaves the other
    end open, and then the answer is None and nothing is scaled.
    """
    begin, begin_abs = parse_time_point(in_point or "", fps)
    end, end_abs = parse_time_point(out_point or "", fps)
    if begin is None or end is None or begin_abs != end_abs or end <= begin:
        return None
    return end - begin


def window_from_points(args, fps=30.0):
    """The same length, out of the In point and Out point of a call."""
    return window_between(getattr(args, "in_point", None),
                          getattr(args, "out_point", None), fps)


def space_needed_mb(audio_paths, video_paths, multitrack, window_s=None):
    """What a run writes, and how much of that goes to the temp folder too.

    Erring upward: every camera is copied and gets audio tracks added,
    plus the processed tracks and the mix. With a window each camera
    carries that stretch and no more, so it shrinks by its own share and
    not by the longest camera's. Both numbers are megabytes.
    """
    video_mb, delivered = 0.0, 0.0
    for p in video_paths:
        try:
            running = float((ffprobe_json(p).get("format")
                             or {}).get("duration") or 0.0)
        except Exception:
            running = 0.0
        share = 1.0
        if window_s and running > 0:
            share = min(1.0, (window_s + 4 * CAMERA_MARGIN_S) / running)
        delivered = max(delivered, running * share)
        video_mb += os.path.getsize(p) / 1e6 * share
    audio_mb = sum(os.path.getsize(p) for p in audio_paths) / 1e6
    # The picture is copied unchanged; what grows the file is the audio,
    # and it is written uncompressed: 48 kHz, 24 bit, two channels are
    # 0.29 MB per second and per track. Counting it from the sizes of the
    # given audio files was far too low wherever the cameras bring their
    # own sound and no separate recording exists at all.
    per_second = 48000 * 3 * 2 / 1e6
    if multitrack:
        # Every camera carries its own mix, its speakers, the overall mix
        # and the camera original. Two plus the speakers is the upper end.
        per_camera = 2 + (len(audio_paths) or 1)
    else:
        per_camera = 2
    added = delivered * per_second * per_camera * max(1, len(video_paths))
    # The processed tracks come back and are mixed once more.
    return (video_mb * 1.05 + added
            + audio_mb * (3.0 if multitrack else 2.0)), added


def space_summary_lines(target, audio_paths, video_paths, multitrack,
                        in_point="", out_point=""):
    """What the run writes and what is free, for the summary before it.

    The size is the preflight's own reckoning, so the two numbers agree
    and a time window shortens both. Only what lands in the target
    folder counts here; the temporary files are the preflight's
    question. Where the disk cannot be read, only the target is named.
    """
    where = target or T('the source folder')
    try:
        needed, _temporary = space_needed_mb(
            audio_paths, video_paths, multitrack,
            window_between(in_point, out_point))
        free = shutil.disk_usage(target or ".").free / 1e6
    except Exception:
        return [T('Target: %s') % where]
    return [TN(len(video_paths),
               'This makes %s video file, about %s. Target: %s',
               'This makes %s video files, about %s. Target: %s')
            % (group_text(len(video_paths)), as_data_size(needed), where),
            T('Free space there: %s') % as_data_size(free)]


def check_disk_space(target_folder, audio_paths, video_paths, multitrack,
                        window_s=None):
    """Report whether there is enough disk space for what will be created.

    Roughly calculated but erring upward, so that a run stops before it
    starts rather than halfway. *window_s* shortens the cameras, so the
    estimate follows it -- generously, or a run that fits is refused.
    """
    folder = target_folder or (os.path.dirname(os.path.abspath(video_paths[0]))
                            if video_paths else os.getcwd())
    while folder and not os.path.isdir(folder):
        fresh = os.path.dirname(folder)
        if fresh == folder:
            break
        folder = fresh
    try:
        free = shutil.disk_usage(folder or ".").free / 1e6
    except Exception:
        return []
    needed, added = space_needed_mb(audio_paths, video_paths, multitrack,
                                    window_s)
    # The temporary files go into the system temp folder, and where that
    # sits on the same disk as the output they eat the same space twice.
    # Counted once the check passed a real run by 1.1 GB and the run
    # died at 88 per cent with nothing said (31.8.2026).
    if on_one_disk(tempfile.gettempdir(), folder or "."):
        needed += added
    # "hint", not "abort": the numbers do fit, and the estimate errs
    # upward, so refusing the run would be wrong. But an estimate that
    # calls itself rough, cleared by one per cent, is not room enough --
    # a real run passed that way and died at 88 per cent.
    kind = ("abort" if free < needed
            else "hint" if free < needed * SPACE_MARGIN else "good")
    advice = ""
    if kind == "abort":
        advice = (T('About %s missing. Free up space or choose another folder '
                 'with --out. The temporary files during the run go '
                 'somewhere else again, into the system temp folder.')
               % as_data_size(needed - free))
    elif kind == "hint":
        advice = T('The estimate is rough, so this is not room enough. Free '
                   'up space or choose another folder with --out.')
    return [Finding(kind, T('Disk space'),
                   T('free %s, about %s needed (%s)')
                   % (as_data_size(free), as_data_size(needed), folder), advice)]


# What the platforms expect as loudness. The podcast directories work with -16
# LUFS for stereo and -19 for mono; YouTube turns loud material down to about
# -14 LUFS but does not turn quiet material up.
PLATFORMS = {
    "podcast": (-16.0, 'Podcast directories, stereo'),
    "podcast-mono": (-19.0, 'Podcast directories, mono'),
    "youtube": (-14.0, 'YouTube -- turns down only, never up'),
    "broadcast": (-23.0, 'EBU R128, broadcast'),
}


def loudness_choices():
    """The loudness targets to pick from: (value, caption).

    The caption carries the number and, in brackets, what that number is
    the standard for. The number on its own says nothing to anybody who
    has not learnt the four by heart, and the brackets are what makes
    the list readable without a manual.

    None is the fifth answer and not a fifth number: nothing of ours
    adjusts at all. auphonic.com goes on doing what its preset says --
    anything else would be a silent remote control of somebody else's
    service -- and without auphonic.com the sound stays as it is in the
    source files.
    """
    out = [(target, "%.0f LUFS (%s)" % (target, T(what_for)))
           for target, what_for in PLATFORMS.values()]
    out.append((None, T('Take from source files')))
    return out


def loudness_answer_file():
    """Where the loudness last chosen in the window is kept."""
    folder = cache_folder()
    return os.path.join(folder, "loudness_target") if folder else ""


def loudness_last():
    """The loudness last chosen in the window; -16 LUFS if never chosen.

    Remembered the way the answer about looking for updates is: one
    small file in the cache folder, and no second mechanism beside it.
    Whoever delivers to the same place every week should not have to
    pick the same entry every week. A project file carrying its own
    value beats this one -- what was saved with a production belongs to
    that production.
    """
    where = loudness_answer_file()
    if not where or not os.path.exists(where):
        return -16.0
    try:
        with open(where, encoding="utf-8") as f:
            text = f.read().strip()
    except OSError:
        return -16.0
    if text == "source":
        return None
    try:
        return float(text)
    except ValueError:
        return -16.0


def loudness_last_set(value):
    """Remember the choice, so it holds for the next new project.

    Returns whether it could be written. Nothing is lost where it
    cannot -- the value is in the window and in the project file -- but
    a caller that wants to know is told rather than left guessing.
    """
    where = loudness_answer_file()
    if not where:
        return False
    try:
        with open(where, "w", encoding="utf-8") as f:
            f.write("source" if value is None else "%g" % value)
    except OSError:
        return False
    return True


def loudness_field_build(into, value):
    """Build the loudness row of the Production box.

    Out here and not inside the window, for the reason
    cut_fields_build gives: the window is long enough without another
    stretch of widget assembly. It is a builder and nothing else --
    the value it binds to comes in, the drop-down comes back.

    It belongs in the Production box, on the page and not behind
    "Settings ...": it is a property of this episode the way the name
    and the output folder are, and whoever delivers somewhere else next
    month has to trip over it rather than go looking for it. Until this
    was built no widget was bound to the loudness at all, and every
    episode out of the window came out at -16 LUFS whatever it was for.
    """
    from PySide6 import QtWidgets as _qw
    row = _qw.QHBoxLayout()
    into.addLayout(row)
    row.addWidget(label(T('Loudness')))
    box = _qw.QComboBox()
    for target, caption in loudness_choices():
        box.addItem(caption, target)
    box.setMinimumWidth(caption_room(box, 300,
                                     [c for _v, c in loudness_choices()]))

    def row_of(want):
        """Which row carries *want*, or -1.

        Compared as a number, not as an object: the same target arrives
        as -16.0 from the list and out of a project file, and one of
        them being an int would put the list on the wrong row.
        """
        for i in range(box.count()):
            here = box.itemData(i)
            if here is None and want is None:
                return i
            if here is not None and want is not None \
                    and abs(here - want) < 0.05:
                return i
        return -1

    def show():
        """Put the stored value onto the list."""
        i = row_of(value.get())
        if i < 0:
            # A value nobody can pick here -- out of a project file
            # written by hand, or by a run with its own --lufs. It is
            # added rather than replaced: opening a project must not
            # quietly change what it was set to.
            box.addItem("%.0f LUFS" % value.get(), value.get())
            i = box.count() - 1
        if box.currentIndex() != i:
            box.setCurrentIndex(i)

    def chosen(*_):
        """The list changed: remember it for the next new project."""
        value.set(box.currentData())
        loudness_last_set(box.currentData())

    box.currentIndexChanged.connect(chosen)
    value.listen(lambda *_: show())
    show()
    speaks_as(box, T('Loudness of the finished episode'))
    # The name of the last entry stands inside the sentence rather than
    # being dropped into a slot: in German it carries an article, and a
    # piece that settles its own case before it knows the slot is how a
    # wrong sentence gets built. Both halves are translated together.
    row.addWidget(hint(
        box,
        T('How loud the finished episode is made. The same gain goes on '
          'every\ntrack, so the balance between the speakers is kept.\n'
          '"Take from source files" adjusts nothing at all: auphonic.com '
          'goes\non doing what its preset says, and without auphonic.com '
          'the sound\nstays as it is in the source files.')))
    row.addStretch(1)
    return box


def lufs_does_nothing(args, videos):
    """Whether --lufs changes anything on the path this run takes.

    Several voices and no picture: the tracks leave as they were
    recorded, because a gain per track would put the voices out of
    balance with each other, and that balance is the one thing that
    path exists to keep. The number still travels to auphonic.com,
    which masters the mix, so a key puts it back in force. One place,
    because the preflight and the run both say it.
    """
    return (not videos and bool(getattr(args, "multitrack", False))
            and getattr(args, "lufs", None) is not None
            and not getattr(args, "auphonic_key", None))


def check_loudness_target(args, videos=()):
    """Report the loudness target in force. It only reports.

    It used to set args.lufs from --platform on the side, and a check
    that quietly changes what it is checking was the cause of the old
    fault: the report and the run could come apart. --platform is gone;
    the four numbers are a list in the window now. Where the number
    does nothing the report says so, or the log names a target that is
    then contradicted further down.
    """
    if getattr(args, "lufs", None) is None:
        return [Finding("good", T('Loudness'),
                       T('taken from the source files, no --lufs given -- '
                         'nothing is adjusted'))]
    near = [n for n, (lufs, _) in PLATFORMS.items() if abs(lufs - args.lufs) < 0.05]
    text = "%.0f LUFS%s" % (args.lufs,
                            "  (%s)" % T(PLATFORMS[near[0]][1]) if near else "")
    if lufs_does_nothing(args, videos):
        return [Finding("good", T('Loudness'),
                       T('%s is set, and nothing is adjusted here: the '
                         'tracks leave as they were recorded, and the '
                         'loudness is set where they are mixed.') % text)]
    return [Finding("good", T('Loudness'), text)]


def check_preset(key, uuid, presetname, lufs, multitrack):
    """Check the chosen preset against what the run needs.

    Uploading costs credit and time, so what would be wrong afterwards has
    to surface first. The preset is read out rather than trusted by name.
    """
    try:
        p = read_preset(key, uuid)
    except Exception as e:
        return [Finding("hint", T('Preset'),
                       T('not readable (%s) -- unchecked.') % str(e)[:60])]
    alg = dict(p.get("algorithms") or {})
    out = [Finding("good", T('Preset'), "%s" % presetname)]
    switched_on = sorted("%s=%s" % (k, v) for k, v in alg.items()
                if v not in (False, None, "", 0))
    out.append(Finding("good", T('Algorithms'),
                       ", ".join(switched_on)[:300] or T('none switched on')))
    target = alg.get("loudnesstarget")
    try:
        target = float(target) if target is not None else None
    except (TypeError, ValueError):
        target = None
    if lufs is None:
        # Nothing of ours adjusts, so there is nothing to compare the
        # preset against: what it masters to is what comes out. That is
        # said, not complained about -- a check with no second value has
        # no verdict to give.
        if target is not None:
            out.append(Finding(
                "good", T('Loudness'),
                T('the preset masters to %s LUFS -- that stands, nothing '
                  'of ours adjusts.') % decimal_text("%.0f" % target)))
    elif target is not None and abs(target - float(lufs)) > 0.05:
        out.append(Finding(
            "abort", T('Loudness'),
            T('the preset masters to %s LUFS, the calculation uses %s.')
            % (decimal_text("%.0f" % target), decimal_text("%.0f" % lufs)),
            T('Both at once does not work: the returning tracks would go '
              'to one value, our own mix to the other. Either set --lufs '
              '%.0f or change the preset.')
            % target))
    if multitrack:
        template = p.get("multi_input_files") or []
        if not template:
            out.append(Finding(
                "abort", T('Track template'),
                T('the Multitrack preset has no track stored.'),
                T('The first preset track sets the settings for all our '
                  'tracks. Otherwise they come back unprocessed. Create a '
                  'track in the preset in the web interface.')))
        else:
            track_alg = dict((template[0].get("algorithms") or {}))
            switched_on = sorted("%s=%s" % (k, v) for k, v in track_alg.items()
                        if v not in (False, None, "", 0))
            out.append(Finding("good", T('per track'),
                               ", ".join(switched_on)[:300] or T('none switched on')))
            if not switched_on:
                out.append(Finding(
                    "hint", "",
                    T('the track template has nothing switched on -- the '
                      'tracks would come back exactly as uploaded.')))
    return out


def report_findings(findings, heading, anyway=False):
    """Print the report. Returns True when the run should be aborted."""
    if not findings:
        return False
    print(as_head(T('\nPREFLIGHT -- %s') % heading))
    for b in findings:
        print(b.line())
        # In the window the finding stands on its file and the advice on
        # the mark. The log has neither, and a count with no findings
        # under it names none of them -- so only the advice is held back.
        if b.advice and not GUI_RUNNING:
            for line in textwrap.wrap(b.advice, 70):
                print("      %s" % line)
    abort = [b for b in findings if b.kind == "abort"]
    hints = [b for b in findings if b.kind == "hint"]
    fixed = [b for b in findings if b.kind == "fixed"]
    parts = [T('%s checked') % group_text(len(findings))]
    if fixed:
        parts.append(TN(len(fixed), '%s fixed on its own',
                        '%s fixed on their own') % group_text(len(fixed)))
    if hints:
        parts.append(TN(len(hints), '%s hint', '%s hints')
                     % group_text(len(hints)))
    if abort:
        parts.append(TN(len(abort), '%s reason to stop',
                        '%s reasons to stop') % group_text(len(abort)))
    print("    %s" % ", ".join(parts))
    if abort and not anyway:
        print(as_bad(T('\nStopped before the first long step. With --anyway '
                       'it runs regardless.')))
        return True
    if abort:
        print(T('    --anyway is set: it runs despite the points above.'))
    return False


def collect_findings(audio_paths, video_paths, fresh=False, crosstalk=True,
                    set_aside=(), apart=(), together=()):
    """Collect all findings about the material.

    Each file is measured and cached individually. Adding a file measures
    only that one; the others are already there. What shows only in
    comparison is derived from the cached data and costs nothing.

    *set_aside* are files that do not take part -- ignored ones, intro,
    outro. They are still checked so their row is not the only one without a
    mark, but they stay out of the comparisons. A colour chart has different
    dimensions from the cameras, and turning that into a hint helps nobody.
    """
    set_aside = {path_key(x) for x in (set_aside or ())}

    def counts_not(findings_, file_path):
        if path_key(file_path) in set_aside:
            for b in findings_:
                b.set_aside = True
        return findings_

    findings, video_data, audio_data = [], [], []
    # The files are measured all at once. Each has its own cache entry
    # and knows nothing of the others, so there is nothing to wait for;
    # what compares them happens below, on the results.
    for p, (b, d) in zip(video_paths, parallel_map(
            video_paths,
            lambda x: measure_cached(x, "video", check_camera_file, fresh))):
        findings += counts_not(b, p)
        if d and path_key(p) not in set_aside:
            video_data.append(d)
    findings += compare_cameras(video_data)
    having_video = [p for p in video_paths if path_key(p) not in set_aside]
    if having_video:
        findings += find_camera_gaps(having_video)
    for p, (b, d) in zip(audio_paths, parallel_map(
            audio_paths,
            lambda x: measure_cached(x, "audio", check_audio_file, fresh))):
        findings += counts_not(b, p)
        if d and path_key(p) not in set_aside:
            audio_data.append(d)
    # Everything comparing audio recordings works with recordings, not with
    # blocks: two blocks of the same recording run one after another, are
    # individually shorter and never overlap.
    audio_paths = [p for p in audio_paths if path_key(p) not in set_aside]
    chains = (group_recording_parts(audio_paths, apart=apart,
                                    together=together)
              if audio_paths else [])
    recordings = by_recording(audio_data, chains)
    findings += compare_audio_tracks(recordings)
    findings += timecode_comparison(video_data + recordings)
    heads = [row[0] for row, _rest in chains]
    if crosstalk and len(heads) > 1:
        # Crosstalk is a statement about the interplay, not about a single
        # file, so it is cached for exactly this set.
        audio_paths = heads
        fingerprint = 'crosstalk_%s' % _fingerprint(audio_paths)
        d = None if fresh else cache_read(fingerprint)
        if d is None:
            try:
                found = check_crosstalk(audio_paths)
            except Exception as e:
                found = [Finding("hint", T('Bleed'),
                                   T('not measurable: %s') % str(e)[:80])]
            d = {"findings": _findings_to_json(found)}
            cache_write(fingerprint, d)
        findings += _findings_from_json(d.get("findings"))
    return findings


def run_preflight(args, audio_paths, video_paths):
    """Run the preflight report on the material. Returns 1 to abort.

    Called once for both modes, before the fork in main(). What needs
    several tracks only checks itself then; everything else applies to a
    single track just as well.
    """
    if getattr(args, "no_preflight", False):
        return 0
    findings = collect_findings(audio_paths, video_paths,
                              bool(getattr(args, "preflight_again", False)),
                              bool(getattr(args, "multitrack", False)),
                              apart=getattr(args, "apart", ()),
                              together=getattr(args, "together", ()))
    # These two depend not on the material but on the call and the machine, so
    # they are determined afresh every time.
    findings += check_disk_space(getattr(args, "out", None), audio_paths, video_paths,
                             bool(getattr(args, "multitrack", False)),
                             window_from_points(args))
    findings += check_loudness_target(args, video_paths)
    return 1 if report_findings(findings, T('does the material fit together?'),
                               getattr(args, "anyway", False)) else 0


def run_ffmpeg_with_progress(cmd, duration, text):
    """Run ffmpeg and show its progress.

    Errors go to a file, not to a pipe. Progress is read from stdout until
    it ends, so an unread stderr pipe would fill up and ffmpeg would stop
    in the middle of the run, waiting for someone to empty it.
    """
    cmd = cmd[:1] + ["-nostats", "-progress", "pipe:1"] + cmd[1:]
    fd, log = tempfile.mkstemp(prefix="vpm_ff_", suffix=".txt")
    os.close(fd)
    try:
        with open(log, "wb") as fh:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=fh)
            # This is where a run spends its minutes, so this is where
            # breaking off has to reach. The child says it is here; the
            # window ends it, and the loop below falls out of itself.
            RUN_STOP["children"].add(proc)
            try:
                show_progress(text, 0.0)
                for line in proc.stdout:
                    share = progress_from_line(line, duration)
                    if share is not None:
                        show_progress(text, share)
                proc.wait()
            finally:
                RUN_STOP["children"].discard(proc)
        if stop_wanted():
            # Ended by us, so the error it left behind says nothing.
            raise Stopped(RUN_STOP["at"] or text)
        show_progress(text, 1.0)
        if THREAD_SHARE.get(threading.get_ident()) is None:
            if OUTPUT_SINK:
                OUTPUT_SINK("\n")
            else:
                sys.stdout.write("\n")
        if proc.returncode:
            with open(log, "r", encoding="utf-8", errors="replace") as fh:
                raise RuntimeError(fh.read()[-2000:])
    finally:
        try:
            os.unlink(log)
        except OSError:
            pass


#--------------------------------------------------------------------- Run

def collect_with_continuations(paths, no_followups, apart=(), together=()):
    """The given files plus their continuations, without duplicates.

    *apart* names blocks that stand on their own, *together* files that
    belong to one recording although their names do not say so -- see
    group_recording_parts.
    """
    apart = FileSet(apart or ())
    joined = ByFile()
    for row in together_chains(together):
        for x in row:
            if x not in apart:
                joined[x] = [y for y in row if y not in apart]
    out, seen, hints = [], set(), []
    for p in paths:
        if os.path.abspath(p) in seen:
            continue
        if p in joined:
            row, discarded = list(joined[p]), []
        elif no_followups or p in apart:
            row, discarded = [p], []
        else:
            row, discarded = find_continuation_files(os.path.abspath(p))
            row = [x for x in row if x not in apart
                   and x not in joined]
        for path in row:
            if os.path.abspath(path) not in seen:
                seen.add(os.path.abspath(path))
                out.append(path)
        hints += discarded
    # Sort by name so the order of selection does not matter: giving only the
    # first block or all three in any order yields the same list. A row
    # forced together by hand is the one thing that keeps its order.
    # --together promises "these files are one recording, in this
    # order", and sorting the row by name would break that promise on
    # every name that is not already alphabetical.
    #
    # The row travels as one block, and the block sorts under the
    # alphabetically smallest name in it. Not under the name given
    # first: the whole point of sorting here is that the order of
    # selection makes no difference, and a block that moved with the
    # order it was typed in would put that difference straight back.
    rank = ByFile()
    for row in together_chains(together):
        row = [x for x in row if x not in apart]
        if not row:
            continue
        smallest = min(os.path.basename(x).lower() for x in row)
        for k, x in enumerate(row):
            rank[x] = (smallest, k)
    out.sort(key=lambda x: rank.get(
        x, (os.path.basename(x).lower(), 0)))
    return out, hints


def build_argument_parser():
    """Define all command line switches."""
    ap = argparse.ArgumentParser(
        prog="videopodcast-magic",
        description="videopodcast-magic %s -- put processed audio into "
                    "video files as the first audio track" % VERSION)
    ap.add_argument("--version", action="version",
                    version="videopodcast-magic %s   %s"
                            % (VERSION, python_note()))
    ap.add_argument("--lang", choices=languages(), default=None,
                    help="language of the messages (default: the system's)")
    ap.add_argument("files", nargs="*",
                    help="audio and video files, told apart by extension. "
                         "Audio only = join and write.")
    ap.add_argument("--out", default=None,
                    help="output folder (default: next to each video)")
    ap.add_argument("--auphonic-api-key", dest="auphonic_key",
                    default=None, metavar="KEY",
                    help="API key from the Auphonic account settings. Turns "
                         "processing on. Without files it only lists the "
                         "presets.")
    ap.add_argument("--auphonic-preset", default=None, metavar="NAME",
                    help="preset name or id (default: asked for)")
    ap.add_argument("--auphonic-wait", dest="auphonic_wait", type=int,
                    default=7200, metavar="SECONDS",
                    help="how long to wait for Auphonic (default: 7200)")
    ap.add_argument("--suffix", default="_audio",
                    help="added to the file name (default: _audio)")
    ap.add_argument("--name-camera", dest="name_camera",
                    default="Camera Original",
                    help="name of the camera track (default: Camera Original)")
    ap.add_argument("--no-camera-audio", dest="no_camera_audio",
                    action="store_true",
                    help="drop the camera's own audio instead of keeping it")
    ap.add_argument("--no-follow-ups", dest="no_follow_ups",
                    action="store_true",
                    help="do not look for numbered continuation files "
                         "(default: they are looked for)")
    ap.add_argument("--apart", action="append", default=[], metavar="FILE",
                    help="this block stands on its own and is not joined "
                         "to a recording, even where its name says it is a "
                         "continuation. May be given several times. The "
                         "interface sets it when a single block is taken "
                         "out of a recording by hand.")
    ap.add_argument("--no-drift", dest="no_drift", action="store_true",
                    help="measure and report clock drift, but do not take "
                         "it out")
    ap.add_argument("--tc", default=None, metavar="HH:MM:SS:FF",
                    help="start timecode of the picture. Used to compare "
                         "against the audio and written into the result. "
                         "Needed where the camera wrote none or a wrong one. "
                         "(default: from the video file)")
    ap.add_argument("--fps", type=float, default=None, metavar="NUMBER",
                    help="frame rate to assume. Decides what a frame is -- "
                         "the frame counts and the threshold above which "
                         "clock drift is taken out. Needed only where "
                         "ffprobe reports a wrong rate. "
                         "(default: from the video file)")
    ap.add_argument("--speech-language", dest="speech_language",
                    default="", metavar="CODE",
                    help="language tag of the audio tracks, three letters "
                         "per ISO 639-2/B -- ger, eng, fra. Careful: ffmpeg "
                         "drops 'deu' silently. Empty means no tag. "
                         "(default: none)")
    ap.add_argument("--speakers-local", dest="speakers_local", default=None,
                    metavar="FILE",
                    help="take exactly that recording apart by voice, "
                         "instead of the one the run would pick itself. A "
                         "run picks a single audio recording, or the "
                         "longest camera track where there is none, and "
                         "takes it apart on its own. What it needs came "
                         "with the program; the run takes minutes. "
                         "(default: whatever the run picks)")
    ap.add_argument("--update", dest="update_now",
                    action="store_true", default=False,
                    help="fetch the newer version and put this one "
                         "beside it as videopodcast_magic.py.old. A run "
                         "only ever says that one is out; nothing is "
                         "fetched without this. (default: off)")
    ap.add_argument("--speakers-from", dest="speakers_from", default=None,
                    metavar="FILE",
                    help="take a finished separation out of a project or "
                         "assignment file instead of computing one. "
                         "(default: none)")
    ap.add_argument("--speakers-count", dest="speakers_count", type=int,
                    default=0, metavar="NUMBER",
                    help="how many people --speakers-local should find. A "
                         "given number improves the recognition and "
                         "quadruples the picture time on the wrong person, "
                         "so it is set only where it is known. "
                         "(default: work it out)")
    ap.add_argument("--no-speakers-local", dest="no_speakers_local",
                    action="store_true",
                    help="never take a recording apart by voice in this "
                         "run, whatever else says so. (default: off)")
    ap.add_argument("--no-speech-recognition", dest="no_speech_recognition",
                    action="store_true",
                    help="do not write down what is said. The cut then has "
                         "no sentence boundaries and the wide shot goes to "
                         "the longest pause nearby. (default: off)")
    ap.add_argument("--no-transcript-file", dest="no_transcript_file",
                    action="store_true",
                    help="write no transcript beside the result. Normally "
                         "the words that were heard go into the output "
                         "folder as json, srt and txt. (default: off)")
    ap.add_argument("--auphonic-resume", dest="auphonic_resume", default=None,
                    choices=("result", "rerun", "adopt", "upload", "abort"),
                    help="what to do when the production is already there: "
                         "result = take the existing one, rerun = compute "
                         "again with the chosen preset without a new upload "
                         "(costs nothing), adopt = the same, but take the "
                         "track names there as speaker names, upload = "
                         "everything again, abort = stop. Without this it "
                         "asks. (default: ask)")
    ap.add_argument("--auphonic-done", dest="auphonic_done", default=None,
                    metavar="FOLDER",
                    help="folder holding tracks Auphonic has already "
                         "processed (files named after the speakers). Then "
                         "nothing is uploaded and no credit is spent -- for "
                         "a second run on the same audio. (default: none)")
    ap.add_argument("--min-edit-duration", dest="min_edit_duration", type=float,
                    default=MIN_EDIT_DURATION_S, metavar="SECONDS",
                    help="shortest a shot may stand. Anything shorter is "
                         "merged into the one that follows; 0 turns it "
                         "off. Three "
                         "seconds is what interview cutting practice asks "
                         "for -- a camera that changes faster than the "
                         "viewer can settle on a face reads as nervous. "
                         "SmartSwitch calls the same thing 1.00, which is "
                         "why this used to be 1.2. (default: 3)")
    ap.add_argument("--min-speech-to-switch", dest="min_speech_to_switch",
                    type=float, default=MIN_SPEECH_TO_SWITCH_S,
                    metavar="SECONDS",
                    help="how long somebody has to hold the floor before "
                         "the camera follows them. Below it the picture "
                         "stays where it is: a short \"yes\" is not a "
                         "change of speaker, and without this the minimum "
                         "edit duration then holds the wrong person on "
                         "screen for seconds. 0 turns it off. (default: "
                         "1.5)")
    ap.add_argument("--silence-hold", dest="silence_hold", type=float,
                    default=SILENCE_HOLD_S, metavar="SECONDS",
                    help="how long a silence may be and still count as a "
                         "breath rather than an end. Only where "
                         "--on-silence hold-brief asks for it: up to here "
                         "the picture stays, beyond it the wide shot "
                         "comes. (default: 1.0)")
    ap.add_argument("--edit-change-delay", dest="delay", type=float,
                    default=0.3, metavar="SECONDS",
                    help="how much later than the audio the picture cuts. "
                         "Negative lets the picture lead. (default: 0.3)")
    ap.add_argument("--reaction-lead", dest="reaction_lead", type=float,
                    default=1.5, metavar="SECONDS",
                    help="how much earlier the picture goes to the answer "
                         "after a question. Only where --on-question asks "
                         "for it. (default: 1.5)")
    ap.add_argument("--reaction-gap", dest="reaction_gap", type=float,
                    default=3.0, metavar="SECONDS",
                    help="how soon the answer has to follow the question "
                         "for the reaction cut to fire. (default: 3)")
    ap.add_argument("--reaction-hold", dest="reaction_hold", type=float,
                    default=0.7, metavar="SHARE",
                    help="how much of the ten seconds after the question "
                         "the answering speaker has to hold, as a share "
                         "between 0 and 1. (default: 0.7)")
    for switch, _caption, default_value, values, _short, _long in CUT_CHOICES:
        ap.add_argument("--" + switch, dest=switch.replace("-", "_"),
                        choices=list(values), default=default_value,
                        help="what is shown where the speech does not say "
                             "it: %s. (default: %s)"
                             % (", ".join(values), default_value))
    ap.add_argument("--wide-after", dest="wide_after", type=float,
                    default=WIDE_AFTER_S, metavar="SECONDS",
                    help="from this hold time on, a shot is broken up by "
                         "leaving the speaker for a while -- placed on a "
                         "sentence boundary nearby, not by the clock. "
                         "0 turns it off. (default: 70)")
    ap.add_argument("--wide-length", dest="wide_length", type=float,
                    default=5.0, metavar="SECONDS",
                    help="how long such an interposed shot stands at "
                         "least; it then runs to the end of the sentence. "
                         "(default: 5)")
    ap.add_argument("--wide-most", dest="wide_most", type=float,
                    default=15.0, metavar="SECONDS",
                    help="how long it stands at most. Where the end of the "
                         "sentence lies beyond it, the last clause break "
                         "before it ends the shot. (default: 15)")
    ap.add_argument("--wide-latest", dest="wide_latest", type=float,
                    default=120.0, metavar="SECONDS",
                    help="upper limit: longest one camera may stand without "
                         "a cut. Where no good pause turns up, it cuts "
                         "anyway. (default: 120)")
    ap.add_argument("--no-wide-edges", dest="no_wide_edges",
                    action="store_true",
                    help="do NOT hold the wide shot at the beginning and the "
                         "end. By default the picture stays wide while the "
                         "greeting and the goodbye are spoken.")
    ap.add_argument("--parallel", type=int, default=0, metavar="COUNT",
                    help="process this many video files at once. 0 = decide "
                         "for me, 1 = one after another. (default: 0)")
    ap.add_argument("--no-metrics", dest="no_metrics", action="store_true",
                    help="measure no metrics at the end and compare no "
                         "camera colours. Saves a few minutes on long "
                         "recordings.")
    ap.add_argument("--intro", default=None, metavar="FILE",
                    help="video file laid over the beginning. It sits on the "
                         "second picture and audio track, so its sound "
                         "carries on under the first words. It is neither "
                         "aligned nor processed. (default: none)")
    ap.add_argument("--outro", default=None, metavar="FILE",
                    help="the same for the end: it starts where the last "
                         "word ends. (default: none)")
    ap.add_argument("--wide-shot", dest="wide_shot", action="append",
                    default=None, metavar="FILE",
                    help="this video file is a wide shot: a camera nobody "
                         "sits in front of. It is filmed, aligned and cut "
                         "to like any other, it just takes no speaker. May "
                         "be given several times. Without it the cameras "
                         "no speaker is assigned to are the wide shots. "
                         "(default: none, so derived)")
    ap.add_argument("--no-single-tracks", dest="no_single_tracks",
                    action="store_true",
                    help="put only the mix into the video, not the single "
                         "recordings beside it. Without Multitrack several "
                         "recordings running at the same time are mixed "
                         "into one track; by default each also goes in on "
                         "its own, unprocessed, so the edit can reach for "
                         "one voice. That costs about 520 MB per track and "
                         "hour.")
    ap.add_argument("--together", action="append", nargs="+",
                    default=[], metavar="FILE",
                    help="these files are one recording, in this order. The "
                         "counterpart to --apart, for blocks the search "
                         "cannot recognise as belonging together -- a "
                         "recorder whose file names carry neither a counter "
                         "nor a clock. Repeatable for several recordings.")
    ap.add_argument("--no-preflight", dest="no_preflight",
                    action="store_true",
                    help="skip the preflight report. By default the material "
                         "is checked before the first long step starts.")
    ap.add_argument("--preflight-again", dest="preflight_again",
                    action="store_true",
                    help="measure the preflight again instead of taking the "
                         "stored measurement. Not needed: a changed file is "
                         "measured again anyway.")
    ap.add_argument("--anyway", action="store_true",
                    help="run even where the preflight found a reason to "
                         "stop.")
    ap.add_argument("--lufs", type=float, default=None,
                    help="loudness the sum of all speaker tracks is brought "
                         "to. The same gain goes on every track, so their "
                         "balance is kept. Usual values: %s. Without it "
                         "nothing is adjusted: the sound is taken from the "
                         "source files as it is, and auphonic.com goes on "
                         "doing what its preset says. (default: none)"
                    % ", ".join("%.0f = %s" % (lufs, what)
                                for lufs, what in PLATFORMS.values()))
    ap.add_argument("--assign", default=None, metavar="FILE",
                    help="JSON file holding which audio track belongs to "
                         "which camera. The interface writes it; this is how "
                         "the assignment reaches a run without it. "
                         "(default: none)")
    ap.add_argument("--without-auphonic", dest="without_auphonic",
                    action="store_true",
                    help="run without auphonic.com: align, mix and write "
                         "locally. The camera cut then comes from a speech "
                         "detection of our own. No de-bleed, no leveler, no "
                         "noise removal.")
    ap.add_argument("--multitrack", action="store_true",
                    help="send every audio file to Auphonic as its own "
                         "track, so the bleed between the microphones can be "
                         "removed. Needs two input tracks -- a recording "
                         "of its own, a channel of a multichannel "
                         "recorder, or the audio of a camera -- and a "
                         "multitrack preset. Which audio belongs to which "
                         "camera comes from --assign; the interface writes "
                         "that file.")
    ap.add_argument("--speech-language-camera", dest="speech_language_camera",
                    default="", metavar="CODE",
                    help="the same for the camera track. Empty means no tag "
                         "-- that is what makes the QuickTime player tell "
                         "the two entries in its audio menu apart at all "
                         "(default: empty)")
    ap.add_argument("--in-point", dest="in_point", default=None, metavar="TIME",
                    help="start of the time window. A timecode like 17:20:14 "
                         "or 17:20:14:00 is absolute, +12:30 or 90 counts "
                         "from the start of the measured window. "
                         "(default: from the video files)")
    ap.add_argument("--out-point", dest="out_point", default=None, metavar="TIME",
                    help="end of the time window, same notation. A negative "
                         "value like -30 counts back from the end. "
                         "(default: from the video files)")
    ap.add_argument("--resolve", action="store_true",
                    help="afterwards create the project in DaVinci Resolve, "
                         "import the finished files and build the timelines. "
                         "Resolve has to be running. (default: off)")
    ap.add_argument("--hdr-check", dest="hdr_check", default=None,
                    metavar="FILE",
                    help="only look: does this finished file carry "
                         "everything that marks it as HDR? Checks primaries, "
                         "curve, matrix, bit depth, codec profile and the "
                         "static metadata. Changes nothing.")
    ap.add_argument("--resolve-json", dest="resolve_json", default=None,
                    metavar="FILE",
                    help="run only the Resolve part, from a "
                         "Production_resolve.json that is already there. "
                         "Then nothing is measured and nothing written.")
    ap.add_argument("--resolve-audio-tracks", dest="resolve_audio_tracks",
                    action="store_true",
                    help="only look: for the project open in Resolve, print "
                         "the audio channel mapping of every clip and the "
                         "tracks of every timeline. Changes nothing.")
    ap.add_argument("--resolve-project", dest="resolve_project", default=None,
                    choices=("update", "keep", "new", "abort"),
                    help="what to do when the Resolve project is already "
                         "there: update = delete both timelines and build "
                         "them again, keep = put the new ones beside them, "
                         "new = a second project alongside, abort = stop. "
                         "Without this it asks.")
    ap.add_argument("--dry-run", action="store_true",
                    help="only measure and report, write nothing")
    # A switch that needs several recordings says so, or it would be
    # taken and do nothing. Marked here rather than at the call site:
    # --help builds its own parser and never reached the old place, so
    # the mark was set and shown to nobody.
    for entry in ap._actions:
        if entry.dest in ONLY_MULTITRACK:
            entry.help = (entry.help or "") + "  [multitrack only]"
    return ap

def main():
    force_utf8_output()
    # Here rather than beside the last line of the file: a run started
    # through the installed command never passes that line.
    watch_outside_calls()
    mark_time("the program is read and running")
    if only_reading(sys.argv[1:]):
        # argparse prints and exits by itself; nothing here needs a tool.
        build_argument_parser().parse_args()
        return 0
    ap = build_argument_parser()
    args = ap.parse_args()
    # The language before the first sentence is made, not before the
    # first one is printed: the complaint about ffmpeg below is written
    # down here and shown much later. Only where one was typed, or the
    # system's language and the one kept from an earlier run are lost.
    if args.lang:
        set_language(args.lang)
    # --update wants no files and no tools, so it is answered before
    # either is looked for -- a broken installation is one of the
    # reasons to reach for it. It is the only way the command line
    # fetches anything.
    if args.update_now:
        return update_from_command_line()
    # Everything this program does goes through ffmpeg, so below the
    # floor there is nothing to start. Behind only_reading() and
    # --update on purpose: --update is the way out of a broken
    # installation and must not fail on the thing it repairs.
    global TOOL_TROUBLE
    TOOL_TROUBLE = find_required_tools()
    mark_time("the tools are found")
    clean_envelope_cache()
    clean_probe_cache()
    clean_preflight_cache()
    # --lang alone is not a job: it only picks the language, so the window
    # still opens. Anything else on the command line means a run.
    rest = list(sys.argv[1:])
    while "--lang" in rest:
        i = rest.index("--lang")
        del rest[i:i + 2]
    rest = [a for a in rest if not a.startswith("--lang=")]
    to_the_window = not rest
    if to_the_window:
        # Qt before the console goes into the log file. It is a hundred
        # megabyte download on a machine that has none, and behind the
        # redirect the terminal would stand silent for minutes and then
        # exit without a word.
        _require_module("PySide6.QtWidgets", "PySide6")
        # Nothing is said here: this path ends in a window, and the
        # program is not started from a console. Where the log is
        # stands in the Help menu instead.
        redirect_console()
        mark_time("the log is open")
    # A place in the program list, laid once and never again. Below the
    # branch on purpose: redirect_console() renames the running log to
    # the backup, so a line written before it lands in the log of the
    # run before, where the Help menu never looks.
    beside("desktop", program=PROGRAM).lay_on_first_start()
    mark_time("the place in the program list is settled")
    if to_the_window:
        return gui()
    force_utf8_output()
    enable_colour_output()
    # Whoever typed a command line has a console, so it is said there --
    # after the language is settled, and before the banner claims a run
    # is starting.
    if TOOL_TROUBLE[0] and not tools_repaired(*TOOL_TROUBLE):
        return 1
    print("videopodcast-magic %s   %s\n%s\n"
          % (VERSION, python_note(), running_from()))
    # Said, not asked. A run started from a script must not stop for a
    # question, and this is not a fault -- only a coarser correction.
    # Where nothing could be done about it, nothing is said either.
    if not soxr_available() and ffmpeg_can_be_had():
        print(as_warn(soxr_note()))
    update_note()
    args.auphonic_done = getattr(args, "auphonic_done", None)
    args.auphonic_resume = getattr(args, "auphonic_resume", None)
    args.production = ""
    args.resolve_project = getattr(args, "resolve_project", None)
    if getattr(args, "hdr_check", None):
        try:
            return check_hdr(args.hdr_check)
        except Exception as e:
            print(T('Stopped: %s') % e)
            return 1
    if getattr(args, "resolve_audio_tracks", False):
        try:
            return print_audio_track_mapping()
        except Exception as e:
            print(T('Stopped: %s') % e)
            return 1
    if getattr(args, "resolve_json", None):
        try:
            return build_resolve_project(args.resolve_json, args.resolve_project,
                                 )
        except Exception as e:
            print(T('Resolve part stopped: %s') % e)
            return 1
    for long in ("no_camera_audio", "no_follow_ups", "no_drift",
                 "dry_run", "multitrack", "resolve"):
        setattr(args, long, getattr(args, long, False))
    args.name_camera = getattr(args, "name_camera", "Camera Original")

    if args.auphonic_key and not args.files:
        try:
            return print_presets(api_key_from_anywhere(args), args.multitrack)
        except Exception as e:
            print(T('Presets could not be loaded: %s') % e)
            return 1
    if not args.files:
        return ap.error(T('No files given.'))
    if args.auphonic_preset:
        e = os.path.splitext(args.auphonic_preset)[1].lower()
        if e in AUDIO_SUFFIXES + VIDEO_SUFFIXES or os.path.exists(args.auphonic_preset):
            args.files.insert(0, args.auphonic_preset)
            args.auphonic_preset = None

    audio_paths, video_paths, other = split_audio_and_video(args.files)
    for p in other:
        print(T('Unknown extension, skipped: %s') % os.path.basename(p))
    if not audio_paths and not video_paths:
        sys.exit(T('No audio file given.'))
    for p in audio_paths + video_paths:
        if not os.path.exists(p):
            sys.exit(T('Not found: %s') % p)

    # Preflight: once for both modes, before any fork.
    if run_preflight(args, audio_paths, video_paths):
        return 1
    if args.multitrack and not audio_paths:
        # Cameras only: their own audio becomes the track. How many
        # tracks that is has to be measured, not counted -- one camera
        # with two clip-on microphones is two of them. So the plan is
        # built first and the decision falls behind it; a camera with
        # one microphone drops into the ordinary path there.
        return multitrack_or_single(args, ap, audio_paths, video_paths)
    if not audio_paths:
        # Picture only, no multitrack: the camera audio becomes the track.
        if len(video_paths) > 1:
            print(T('Several cameras but no audio file. Each camera would '
                    'have its own audio --\nthat is what --multitrack is '
                    'for. Otherwise one camera after another.'))
            return 1
        args._camera_audio = tempfile.mkdtemp(prefix="vpm_camaudio_")
        atexit.register(shutil.rmtree, args._camera_audio, True)
        try:
            audio_paths = [extract_audio_from_video(video_paths[0], args._camera_audio)]
        except Exception as e:
            print(T('Camera audio not usable: %s') % e)
            return 1
        print()
    missing = check_mode_fits_input(audio_paths, args)
    if missing:
        print(missing)
        return 1
    # One way in, whatever --multitrack says. The switch decides how the
    # recordings are grouped, and nothing else -- not which time axis is
    # built, not which arithmetic places the window, not which code
    # writes the files. One axis for one job.
    return multitrack_or_single(args, ap, audio_paths, video_paths)


#------------------------------------------------ Beside the window
# Named here rather than inside the interface section: none of them
# touches a widget, and other sections reach in for them.


def stand_in_camera(names):
    """What stands in front of a silence where no camera is a wide shot.

    Not a wide shot, and it must not act as one: everything the wide
    shot settings ask for is switched off wherever this is used.

    All that matters here is that the preview and the run reach for the
    same camera -- and they did not. The preview took the first of its
    own list, the run took the reference clip, and in a real shoot both
    are real cameras, so it showed as two different cuts rather than as
    a fault. Found 25.8.2026, and only reachable at all since a camera
    with a speaker stopped counting as a wide shot.

    By name, not by position: the two lists are built in different
    places and nothing says they are sorted alike, so a rule that hangs
    on the order would let them drift again on the day one of them is
    built differently.
    """
    return sorted(n for n in names if n)[:1] or ["Wide"]


def common_window(camera_areas):
    """The stretch every camera saw, and the two that decide it.

    *camera_areas* is (from, to, name) per camera, in reference camera
    time. Returns (t0, begins_with, t1, ends_with).

    Every camera, not any camera. A window wider than a camera reaches
    has a stretch where a cut to that camera finds no picture, and the
    episode then comes out shorter than the window said it would.
    Measured on 26.8.2026 over the test interview: the beginning lay
    12.567 s before one of three cameras began, and on the fixture the
    window even began at -0.180 s -- before its own zero. Whoever wants
    that stretch anyway sets an In point of their own; what is derived
    is a window every camera can fill. Decided on 29.8.2026.

    Sitting out here rather than inside the run because it is
    arithmetic and nothing else, and arithmetic can be held against
    numbers without building a window and an hour of sound first.
    """
    t0, begins_with = max((x, name) for x, _y, name in camera_areas)
    t1, ends_with = min((y, name) for _x, y, name in camera_areas)
    return t0, begins_with, t1, ends_with


def finished_tracks_find(base):
    """Report whether processed tracks from Auphonic are already there.

    After a run the output folder holds a subfolder with the single tracks.
    Choosing the same folder again usually means reassembling rather than
    uploading again, so it is offered.
    """
    if not base or not os.path.isdir(base):
        return None
    for name in ("auphonic-tracks",):
        p = os.path.join(base, name)
        if os.path.isdir(p) and any(
                os.path.splitext(f)[1].lower() in AUDIO_SUFFIXES
                for f in os.listdir(p)):
            return p
    return None


MARK_DE = "**Deutsch**"


# What separates the two halves of a release text. Each version says
# everything twice: the English part first, the German part under this
# line. Two strings in one place -- the changelog writes them, the
# window looks for them, and the release test insists on them.
MARK_EN = "**English**"


def release_text_in(text, language=None):
    """Keep the half of a release text that is in this language.

    From 2.20.0-beta on a release says everything twice, in two blocks
    one under the other: English first, German under a line of its own.
    Both belong on the release page, where anybody may read and jump to
    the language they want. In the window only one is wanted -- two
    languages in a box are twice as long and half as readable.

    Given away only where the mark is really there. A text from before
    this, or one where the mark was forgotten, comes back whole: half a
    text is worse than one in the wrong language.
    """
    lines = str(text or "").split("\n")
    at = [i for i, x in enumerate(lines) if x.strip() == MARK_DE]
    if not at:
        return text
    if (language or LANG) == "de":
        kept = lines[at[0] + 1:]
    else:
        kept = lines[:at[0]]
        # The rule that draws the line between them goes with it.
        while kept and kept[-1].strip() in ("", "---", "***", "___"):
            kept.pop()
    return "\n".join(x for x in kept
                      if x.strip() not in (MARK_EN, MARK_DE)).strip()


class Stopped(Exception):
    """The run was broken off from the window."""


# What is running right now, so that breaking off can end it. A flag on
# its own would not do: the run spends most of its minutes waiting for
# ffmpeg, and a child nobody tells goes on writing long after the window
# says it has stopped.
RUN_STOP = {"wanted": False, "children": set(), "at": ""}


def stop_wanted():
    """Whether somebody has asked for the run to stop."""
    return bool(RUN_STOP["wanted"])



#-------------------------------------------------------- The separation
# A piece of its own, in the folder "speakers" beside this one. Read
# here and not where it is first used, because the cut and the window
# bind names out of it: this line stands before the two that read them.

# Measured once and kept: importing pyannote takes seconds, and the
# question is asked wherever a separation might be wanted. forget_
# speaker_split() throws it away, because after an install the answer
# from before it is about an installation that is gone.

# The two stay here because the separation rebinds them as it runs.
# A copy in the piece would go stale under a name bent from outside,
# so it reads and writes them through the program.
_SPEAKER_READY = None
_SPEAKER_WHY = ""

speakers = beside("speakers", program=PROGRAM)
take_from(speakers)

# Nothing in this file calls into the separation, so nothing is
# written out here: what the piece brings answers under this program
# through take_from above, and that is what the cut and the window
# bind out of it.


#---------------------------------------------------------- The project
# A piece of its own, in the folder "resolve" beside this one. Read
# here and not where it is first used, because it binds what it takes
# out of this file: Finding above is the last of that.

resolve = beside("resolve", program=PROGRAM)
take_from(resolve)

# What this file itself calls out of the project building. The rest of
# what it brings answers here too, through take_from above; these are
# written out because they are read in this file, and a name read here
# and bound nowhere here is a loose end.
CLIP_COLOURS = resolve.CLIP_COLOURS
CLIP_COLOURS_RGB = resolve.CLIP_COLOURS_RGB
CLIP_COLOURS_RGB_DARK = resolve.CLIP_COLOURS_RGB_DARK
CLIP_COLOURS_RGB_LIGHT = resolve.CLIP_COLOURS_RGB_LIGHT
MATRIX_BT2020 = resolve.MATRIX_BT2020
ON_DARK = resolve.ON_DARK
PRIMARIES_BT2020 = resolve.PRIMARIES_BT2020
build_resolve_project = resolve.build_resolve_project
camera_text = resolve.camera_text
check_hdr = resolve.check_hdr
colour_per_camera = resolve.colour_per_camera
colour_text = resolve.colour_text
file_frame_rate = resolve.file_frame_rate
frames_to_timecode = resolve.frames_to_timecode
hdr_from_sources = resolve.hdr_from_sources
known_frame_rate = resolve.known_frame_rate
own_frame_rate = resolve.own_frame_rate
print_audio_track_mapping = resolve.print_audio_track_mapping
resolve_timeline_rate = resolve.resolve_timeline_rate
seconds_to_frames = resolve.seconds_to_frames
timecode_to_frames = resolve.timecode_to_frames
timeline_frame_rate = resolve.timeline_frame_rate


#-------------------------------------------------------------- The cut
# A piece of its own, in the folder "cut" beside this one. Read here
# and not where it is first used, because the window binds names out
# of it: this line has to stand before the one that reads the window.

cut = beside("cut", program=PROGRAM)
take_from(cut)

# What this file itself calls out of the cutting. The rest of what it
# brings answers here too, through take_from above; these are written
# out because they are read in this file, and a name read here and
# bound nowhere here is a loose end.
MIN_SPEECH_TO_SWITCH_S = cut.MIN_SPEECH_TO_SWITCH_S
WIDE_AFTER_S = cut.WIDE_AFTER_S
finish_without_auphonic = cut.finish_without_auphonic
is_stand_in_name = cut.is_stand_in_name
roles_report = cut.roles_report
separation_for_run = cut.separation_for_run
speakers_for_the_cut = cut.speakers_for_the_cut
speakers_from_tracks = cut.speakers_from_tracks
voice_names_report = cut.voice_names_report
who_asks = cut.who_asks
write_cut_list = cut.write_cut_list
write_handover = cut.write_handover
write_metrics_csv = cut.write_metrics_csv


#-------------------------------------------------------- The interface
# A piece of its own, in the folder "ui" beside this one. Read here and
# not where it is first used, because it binds what it takes out of
# this file: all of that has to stand before this line.

ui = beside("ui", program=PROGRAM)
take_from(ui)
pieces_answer_together()

# What this file itself calls out of the window. The rest of what the
# window brings answers here too, through take_from above; these are
# written out because they are read in this file, and a name read here
# and bound nowhere here is a loose end.
caption_room = ui.caption_room
cells_laid_out = ui.cells_laid_out
choices_shut = ui.choices_shut
gui = ui.gui
hint = ui.hint
label = ui.label
speaks_as = ui.speaks_as


# ---------------------------------------------------------------------------
# Catalogue
# ---------------------------------------------------------------------------
# Every message of this program in the other languages stands in a file
# of its own beside this one. How to add a language: see the top.

CATALOGUE["de"] = texts_of_language("de")
# German is complete; the seven after it are partial, and every text
# they leave out appears in English. Arabic is translated and stands
# beside them, but is not offered: the window never sets a reading
# direction, so it would come out left to right.
CATALOGUE["es"] = texts_of_language("es")
CATALOGUE["pt"] = texts_of_language("pt")
CATALOGUE["fr"] = texts_of_language("fr")
CATALOGUE["ru"] = texts_of_language("ru")
CATALOGUE["zh"] = texts_of_language("zh")
CATALOGUE["ja"] = texts_of_language("ja")
CATALOGUE["hi"] = texts_of_language("hi")

# Where the window's language comes from: what somebody chose in an
# earlier run, and the system where nobody has chosen yet. --lang beats
# both, and main() applies it once the command line has been read.
LANG = set_language(kept_language() or system_locale())


if __name__ == "__main__":
    sys.exit(main())
