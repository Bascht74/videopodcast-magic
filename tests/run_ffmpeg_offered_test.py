# -*- coding: utf-8 -*-
"""Getting ffmpeg is offered on all three systems, and a test run gets none.

The floor and what is refused below it are measured in
run_ffmpeg_new_enough_test.py. This is the other half: that every one
of the three systems has a way of getting one, that soxr is said and
never demanded, and that a run marked as a test opens no connection
and keeps no folder.

The sections in order: a way on every system; what a test run may do,
which is nothing; the note about soxr following the measurement rather
than the hope; that an install throws the old measurement away before
it reports; and what an archive is allowed to give up, which is the
two programs, runnable, and nothing else. Whether a file may be run is
asked of each system in its own terms -- Unix answers with the owner's
execute bit, Windows with the ending, and a mode says nothing there.
No connection is ever opened -- the one function that would open it is
replaced, so what is measured is what the program does with the answer.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import io
import lzma
import shutil
import sys
import tarfile
import tempfile
import time
import zipfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
m = the_program.load()
m.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


class OnlyBrew:
    """A search path with brew on it and nothing else."""

    @staticmethod
    def which(name, path=None):
        return "/opt/homebrew/bin/brew" if name == "brew" else None


class NoTool:
    """A search path with nothing on it at all."""

    @staticmethod
    def which(name, path=None):
        return None


def driven(platform_name, machine, tools=NoTool):
    """Run the program's questions as though it stood on that machine.

    sys.platform and platform.machine() are the two the answers hang
    on, and both are read out of modules the program shares with this
    test -- so they are put back in a finally, whatever happens.
    """
    was = (m.sys.platform, m.platform.machine, m.shutil,
           m.brew_ffmpeg_from_elsewhere)
    m.sys.platform = platform_name
    m.platform.machine = lambda: machine
    m.shutil = tools()
    m.brew_ffmpeg_from_elsewhere = lambda: False
    try:
        return (m.ffmpeg_build_url(), m.ffmpeg_can_be_had(),
                m.how_to_get_ffmpeg(), " ".join(m.package_manager_command()))
    finally:
        (m.sys.platform, m.platform.machine, m.shutil,
         m.brew_ffmpeg_from_elsewhere) = was


#------------------------------------------- 1. A way on every system

print("1. Every one of the three systems has a way of getting ffmpeg")

linux = driven("linux", "x86_64")
linux_arm = driven("linux", "aarch64")
windows = driven("win32", "AMD64")
windows_arm = driven("win32", "ARM64")
mac = driven("darwin", "arm64", OnlyBrew)

# The name of the archive, not the whole address: what the address is
# built out of stands in one place in the program, and holding the
# ending against it here would only repeat that place.
def archive(url):
    return url.rsplit("/", 1)[-1]


check("Linux is offered a built ffmpeg to fetch",
      archive(linux[0]) == "ffmpeg-n9.0-latest-linux64-gpl-9.0.tar.xz",
      "it names %r, wanted the linux64 archive -- what a distribution "
      "holds is under the floor, Ubuntu 24.04 carries 6.1.1"
      % (archive(linux[0]),))
check("Windows is offered a built ffmpeg to fetch",
      archive(windows[0]) == "ffmpeg-n9.0-latest-win64-gpl-9.0.zip",
      "it names %r, wanted the win64 archive -- Windows has no package "
      "manager to ask at all" % (archive(windows[0]),))
check("an arm machine is offered the build for its own processor",
      archive(linux_arm[0]) == "ffmpeg-n9.0-latest-linuxarm64-gpl-9.0.tar.xz"
      and archive(windows_arm[0])
      == "ffmpeg-n9.0-latest-winarm64-gpl-9.0.zip",
      "arm Linux %r, arm Windows %r"
      % (archive(linux_arm[0]), archive(windows_arm[0])))
# A machine nothing is built for gets no address at all: an address
# that answers 404 is worse than a sentence saying where to look.
narrow = driven("linux", "i386")
check("a 32-bit machine is offered no build that does not exist",
      narrow[0] == "",
      "it names %r, wanted nothing" % (narrow[0],))
# Measured 4.9.2026: there is no native arm64 macOS build to fetch, and
# this program does not run under Rosetta. So a Mac compiles, which is
# minutes, and that is the price of the finer correction there.
check("a Mac is offered no build to fetch but one to compile",
      mac[0] == "" and "homebrew-ffmpeg/ffmpeg/ffmpeg" in mac[3],
      "it names the address %r and the command %r" % (mac[0], mac[3]))
check("all three answer that ffmpeg can be had here",
      [linux[1], windows[1], mac[1]] == [True, True, True],
      "Linux %r, Windows %r, macOS %r" % (linux[1], windows[1], mac[1]))
check("and all three name in words what would happen",
      all(x[2] for x in (linux, windows, mac)),
      "Linux %r, Windows %r, macOS %r"
      % (linux[2][:40], windows[2][:40], mac[2][:40]))
# A Mac without brew can do nothing by itself, and then there is no
# button -- only a sentence saying where to look.
bare = driven("darwin", "arm64", NoTool)
check("a Mac with no package manager is offered no button, only advice",
      bare[1] is False and bool(bare[2]),
      "can be had %r, advice %r" % (bare[1], bare[2][:60]))


#------------------------------------------ 2. What a test run may do

print("\n2. A test run fetches nothing and keeps nothing")

opened = []


def no_connection(url, where, say=None):
    opened.append(url)
    return "the test opened no connection"


was_fetch, was_folder = m.fetch_archive, m.tools_folder
was_silent = os.environ.get("VPM_SILENT")
os.environ["VPM_SILENT"] = "1"
ROOM = tempfile.mkdtemp(prefix="vpm_toolsroom_")
try:
    m.fetch_archive = no_connection
    # Two things stop a test run from fetching: this guard, and the
    # folder it would put a build in, which a test run is not given.
    # The second is driven out of the way here, or it would repair the
    # first and the check below could not fall.
    m.tools_folder = lambda make=False: ROOM
    was = (m.sys.platform, m.platform.machine)
    m.sys.platform, m.platform.machine = "linux", (lambda: "x86_64")
    try:
        silent_answer = m.fetch_ffmpeg_build(asked=True)
        m.tools_folder = was_folder
        silent_folder = m.tools_folder(make=True)
    finally:
        m.sys.platform, m.platform.machine = was
finally:
    m.fetch_archive, m.tools_folder = was_fetch, was_folder
    shutil.rmtree(ROOM, ignore_errors=True)
    if was_silent is None:
        os.environ.pop("VPM_SILENT", None)
    else:
        os.environ["VPM_SILENT"] = was_silent

check("a test run opens no connection to fetch ffmpeg",
      not opened and silent_answer is False,
      "%d addresses opened, wanted 0: %s -- and the answer was %r"
      % (len(opened), opened[:2], silent_answer))
check("and it is given no folder to keep one in",
      silent_folder is None,
      "the folder was %r, wanted none -- a hundred and fifty megabytes "
      "in the cache of whoever ran the suite" % (silent_folder,))

# The soft offer is the new box, and it must not come up in a test run
# either. It is driven through a message box that presses nothing.
class Box:
    made = []

    def __init__(self, parent):
        self.buttons = []
        Box.made.append(self)

    def setWindowTitle(self, text):
        pass

    def setText(self, text):
        self.shown = text

    def setInformativeText(self, text):
        pass

    def addButton(self, text, role):
        self.buttons.append(text)
        return text

    def exec(self):
        return 0

    def clickedButton(self):
        return None


Box.AcceptRole, Box.RejectRole = 0, 1


class Widgets:
    QMessageBox = Box


was_qt, was_soxr = m._qt_widgets, m._SOXR
os.environ["VPM_SILENT"] = "1"
try:
    m._qt_widgets = lambda: Widgets
    m._SOXR = False
    Box.made = []
    quiet_offer = m.soxr_offer(None)
    quiet_boxes = len(Box.made)
finally:
    m._qt_widgets, m._SOXR = was_qt, was_soxr
    if was_silent is None:
        os.environ.pop("VPM_SILENT", None)
    else:
        os.environ["VPM_SILENT"] = was_silent

check("and no box offers it a finer build either",
      quiet_offer is False and quiet_boxes == 0,
      "%d boxes came up, wanted 0, and the offer answered %r"
      % (quiet_boxes, quiet_offer))


#---------------------------------- 3. The note follows the measurement

print("\n3. What is said about soxr is what was measured")

was_have = m._have_soxr
try:
    m._have_soxr = lambda: True
    m.forget_soxr()
    with_soxr = m.soxr_note()
    m._have_soxr = lambda: False
    m.forget_soxr()
    without_soxr = m.soxr_note()
finally:
    m._have_soxr = was_have
    m.forget_soxr()

check("a build with soxr is reported as one",
      with_soxr == m.T('This ffmpeg has soxr: the clock drift between '
                       'cameras comes out in steps of 0.21 ppm.'),
      "it said %r" % (with_soxr[:70],))
check("a build without soxr is not reported as one",
      without_soxr == m.T('This ffmpeg has no soxr: the clock drift '
                          'between cameras comes out in steps of 21 ppm '
                          'instead of 0.21.'),
      "it said %r" % (without_soxr[:70],))


#-------------------------------- 4. An install measures again, from new

print("\n4. After installing, what arrived is asked and not claimed")

# The kept answer is what makes this worth a check: it is measured
# once and remembered, so without throwing it away the program would
# report the build that has just been replaced.
answers = [True, False]
was_manager, was_find = m.install_over_package_manager, m.find_required_tools
try:
    m._have_soxr = lambda: answers.pop(0) if answers else False
    m.forget_soxr()
    before = m.soxr_available()
    m.install_over_package_manager = lambda *a, **k: True
    m.find_required_tools = lambda: ("", "")
    took = m.install_ffmpeg(asked=True)
    after = m.soxr_available()
finally:
    (m._have_soxr, m.install_over_package_manager,
     m.find_required_tools) = was_have, was_manager, was_find
    m.forget_soxr()

check("an install that worked is reported as one",
      took is True, "install_ffmpeg answered %r" % (took,))
check("and the soxr answer measured before it is thrown away",
      before is True and after is False,
      "before the install %r, after it %r -- wanted True then False, "
      "because the second measurement is about the build that arrived"
      % (before, after))


#------------------------------------- 5. What an archive may give up

print("\n5. An archive gives up the two programs and nothing else")

WORK = tempfile.mkdtemp(prefix="vpm_ffbuild_")
# The two programs are called ffmpeg.exe and ffprobe.exe in the Windows
# build and carry no ending anywhere else -- and that ending is what
# Windows starts a file by. So the archive here is shaped like the one
# this system really gets, and the last question below is asked about a
# file that could really run.
EXE = ".exe" if sys.platform == "win32" else ""
BOTH = ["ffmpeg" + EXE, "ffprobe" + EXE]
INSIDE = ["build/bin/ffmpeg" + EXE, "build/bin/ffprobe" + EXE,
          "build/bin/ffplay" + EXE,
          "build/doc/general.html", "build/LICENSE.txt",
          # A path that tries to climb out of the folder it is
          # unpacked into. Nothing in an archive may decide where a
          # file lands, so this one has to end up beside the others.
          # One step up and no more, so that a broken version writes
          # into the test's own folder and not into the machine.
          "../ffmpeg" + EXE]


def may_be_started(path):
    """The system's own answer to whether that file can be run.

    Unix hangs it on the owner's execute bit, and os.access asks the
    kernel for that rather than reading a mode here. Windows hangs it
    on the ending instead: os.chmod sets only the read-only flag there
    and the mode comes back 0o666 whatever was asked for, so a mode is
    no answer to this question at all.
    """
    if sys.platform == "win32":
        return os.path.isfile(path) and path.lower().endswith(".exe")
    return os.access(path, os.X_OK)


def build_zip(where):
    with zipfile.ZipFile(where, "w") as zf:
        for name in INSIDE:
            zf.writestr(name, b"not really a program\n")
    return where


def build_tar(where):
    plain = os.path.join(WORK, "plain.tar")
    with tarfile.open(plain, "w") as tf:
        for name in INSIDE:
            info = tarfile.TarInfo(name)
            info.size = 21
            tf.addfile(info, io.BytesIO(b"not really a program\n"))
    with open(plain, "rb") as raw, lzma.open(where, "wb") as out:
        shutil.copyfileobj(raw, out)
    return where


try:
    out_zip = os.path.join(WORK, "out_zip")
    out_tar = os.path.join(WORK, "out_tar")
    os.makedirs(out_zip)
    os.makedirs(out_tar)
    from_zip = m.unpack_tools(build_zip(os.path.join(WORK, "b.zip")),
                              out_zip)
    from_tar = m.unpack_tools(build_tar(os.path.join(WORK, "b.tar.xz")),
                              out_tar)
    left_zip = sorted(os.listdir(out_zip))
    left_tar = sorted(os.listdir(out_tar))
    outside = os.path.exists(os.path.join(WORK, "ffmpeg" + EXE))
    runnable = [may_be_started(os.path.join(out_zip, n)) for n in left_zip]
    modes = [oct(os.stat(os.path.join(out_zip, n)).st_mode & 0o777)
             for n in left_zip]
finally:
    shutil.rmtree(WORK, ignore_errors=True)

check("a zip gives up ffmpeg and ffprobe and nothing beside them",
      left_zip == BOTH and from_zip == 3,
      "it left %r behind and reported %d files, wanted %r and 3 -- "
      "ffplay, the documentation and the licence are 150 MB of what "
      "nobody asked for" % (left_zip, from_zip, BOTH))
check("a tar gives up the same two and nothing beside them",
      left_tar == BOTH and from_tar == 3,
      "it left %r behind and reported %d files, wanted %r and 3"
      % (left_tar, from_tar, BOTH))
check("a path in the archive cannot decide where a file lands",
      outside is False,
      "an entry called %r was written outside the folder it was "
      "unpacked into" % (INSIDE[-1],))
check("and what is unpacked may be started on this system",
      runnable == [True, True],
      "on %s the two answered %r under the names %r, with the modes %r "
      "-- wanted both runnable: a file out of an archive carries no "
      "permission and no ending anybody can rely on, so the program has "
      "to give it what this system starts a file by"
      % (sys.platform, runnable, left_zip, modes))


print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
