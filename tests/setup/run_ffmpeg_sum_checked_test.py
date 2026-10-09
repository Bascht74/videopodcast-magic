# -*- coding: utf-8 -*-
"""A fetched ffmpeg build is unpacked only when the program's own sum fits.

The build is somebody else's, and before this was held against anything
a stand-in whose ffmpeg was a shell script was reported as a success.
A list of sums fetched from beside the build can be swapped with it, so
the program names one fixed build, carries its sum itself and asks the
network for the archive alone. The cases in order: every build offered
is a named one with its sum in the program; the sum fits, the two
programs arrive and nothing but the archive was fetched; the sum
differs, the program carries none for the archive, or the archive holds
ffmpeg twice -- and in each of those nothing lands in the tools folder,
the archive is gone again, and the reason is said. The one function
that opens a connection is replaced and the sockets are shut besides,
so nothing here goes outside.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program
SCRIPT = the_program.SCRIPT
import hashlib
import io
import lzma
import re
import shutil
import socket
import tarfile
import tempfile
import time

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


WORK = tempfile.mkdtemp(prefix="vpm_sumcheck_")
BODY = b"not really a program\n"


def build_tar(where, inside):
    """A tar.xz shaped like the Linux build, with these entries in it."""
    plain = where + ".plain"
    with tarfile.open(plain, "w") as tf:
        for name in inside:
            info = tarfile.TarInfo(name)
            info.size = len(BODY)
            tf.addfile(info, io.BytesIO(BODY))
    with open(plain, "rb") as raw, lzma.open(where, "wb") as out:
        shutil.copyfileobj(raw, out)
    os.remove(plain)
    with open(where, "rb") as f:
        return f.read()


GOOD = build_tar(os.path.join(WORK, "good.tar.xz"),
                 ["build/bin/ffmpeg", "build/bin/ffprobe",
                  "build/bin/ffplay", "build/LICENSE.txt"])
TWICE = build_tar(os.path.join(WORK, "twice.tar.xz"),
                  ["build/bin/ffmpeg", "build/bin/ffprobe", "other/ffmpeg"])
# The addresses are asked of the program for the four machines a build
# exists for, not written here: they move with every build it names.
MACHINES = (("linux", "x86_64"), ("linux", "aarch64"),
            ("win32", "AMD64"), ("win32", "ARM64"))
was_machine = (m.sys.platform, m.platform.machine)
offered = {}
try:
    for system, machine in MACHINES:
        m.sys.platform = system
        m.platform.machine = lambda machine=machine: machine
        offered["%s %s" % (system, machine)] = m.ffmpeg_build_url()
finally:
    m.sys.platform, m.platform.machine = was_machine
URL = offered["linux x86_64"]
ARCHIVE = URL.rsplit("/", 1)[-1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def outside(address):
    raise OSError("the test shut the network: %r" % (address,))


def run(served, sums):
    """fetch_ffmpeg_build on a Linux machine against that stand-in release.

    *served* maps an address to the bytes it answers with; any other
    address answers like a missing file. *sums* stands in for the sums
    the program carries, because the archive served is a stand-in and
    not the real build. Returns what it answered, what lay in the tools
    folder afterwards, whether a fetched file was left on disk, the
    addresses asked, and everything it said.
    """
    room = tempfile.mkdtemp(prefix="vpm_tools_", dir=WORK)
    asked, kept, said = [], [], []

    def fetch(url, where, say=None):
        asked.append(url)
        if url not in served:
            return "HTTP Error 404: Not Found (the test's stand-in)"
        with open(where, "wb") as out:
            out.write(served[url])
        kept.append(where)
        return ""

    was = (os.environ.pop("VPM_SILENT", None), os.environ.get("PATH"),
           m.sys.platform, m.platform.machine, m.fetch_archive,
           m.tools_folder, m.open_page, m.FFMPEG_BUILD_SUMS,
           socket.socket.connect, socket.create_connection)
    try:
        m.sys.platform, m.platform.machine = "linux", (lambda: "x86_64")
        m.fetch_archive = fetch
        m.tools_folder = lambda make=False: room
        m.open_page = lambda url: False
        m.FFMPEG_BUILD_SUMS = sums
        socket.socket.connect = lambda one, address, *rest: outside(address)
        socket.create_connection = lambda address, *rest, **more: \
            outside(address)
        answer = m.fetch_ffmpeg_build(asked=True, say=said.append)
    finally:
        (silent, path, m.sys.platform, m.platform.machine, m.fetch_archive,
         m.tools_folder, m.open_page, m.FFMPEG_BUILD_SUMS,
         socket.socket.connect, socket.create_connection) = was
        if silent is not None:
            os.environ["VPM_SILENT"] = silent
        if path is not None:
            os.environ["PATH"] = path
        m.forget_soxr()
    # The folder's own name is this run's and nobody else's, so the
    # line that goes into a report carries a word in its place.
    return (answer, sorted(os.listdir(room)),
            [os.path.basename(k) for k in kept if os.path.exists(k)],
            asked, "".join(said).replace(room, "<tools folder>"))


try:
    url = URL
    OTHER = "ffmpeg-another-build-win64-gpl.zip"
    fits = run({url: GOOD}, {OTHER: sha(b"x"), ARCHIVE: sha(GOOD)})
    wrong = run({url: GOOD}, {ARCHIVE: sha(b"other")})
    unnamed = run({url: GOOD}, {OTHER: sha(GOOD)})
    twice = run({url: TWICE}, {ARCHIVE: sha(TWICE)})
finally:
    shutil.rmtree(WORK, ignore_errors=True)

print("1. Every build offered is a named one, with its sum in the program")
# "latest" is the tag BtbN moves to each new build: a sum written here
# against it would be wrong the next morning.
moving = sorted(u for u in offered.values() if "latest" in u)
check("no build offered comes off the moving latest tag",
      not moving and "" not in offered.values(),
      "%d of %d addresses name it, %d are empty: %r"
      % (len(moving), len(offered), list(offered.values()).count(""),
         moving or offered))
unsummed = sorted(
    "%s: %r" % (machine, m.FFMPEG_BUILD_SUMS.get(u.rsplit("/", 1)[-1]))
    for machine, u in offered.items()
    if not re.fullmatch(r"[0-9a-f]{64}",
                        m.FFMPEG_BUILD_SUMS.get(u.rsplit("/", 1)[-1]) or ""))
check("every build offered has its sum written in the program",
      not unsummed,
      "%d of %d machines with no SHA-256 for their archive: %s"
      % (len(unsummed), len(offered), "; ".join(unsummed)))

print("\n2. A build whose sum fits is unpacked")
check("a build whose listed sum fits is unpacked and reported",
      fits[0] is True and fits[1] == ["ffmpeg", "ffprobe"],
      "it answered %r and left %r in the tools folder, wanted True and "
      "ffmpeg, ffprobe -- asked %r, said %r"
      % (fits[0], fits[1], fits[3], fits[4][-200:]))
check("and nothing is fetched but the build itself",
      fits[3] == [URL],
      "it asked %r, wanted only %r" % (fits[3], URL))

print("\n3. A build that does not fit is refused, and says why")
check("a build whose sum differs is refused and nothing unpacked",
      wrong[0] is False and wrong[1] == [],
      "it answered %r and left %r in the tools folder, wanted False and "
      "nothing -- said %r" % (wrong[0], wrong[1], wrong[4][-200:]))
check("and the refusal names the sum listed and the sum that came",
      m.T('The build does not match its checksum, so it was not unpacked: '
          '%s listed, %s arrived.') % (sha(b"other"), sha(GOOD))
      in wrong[4],
      "it said %r" % (wrong[4][-300:],))
check("and the refused archive is not left lying on disk",
      wrong[2] == [],
      "%r still there after the refusal" % (wrong[2],))
check("a build is refused when the program carries no sum for it",
      unnamed[0] is False and unnamed[1] == []
      and m.T('The list of checksums does not name %s, so the build was '
              'not unpacked.') % ARCHIVE in unnamed[4],
      "it answered %r, left %r in the tools folder, said %r"
      % (unnamed[0], unnamed[1], unnamed[4][-300:]))
check("a build holding ffmpeg twice is refused though its sum fits",
      twice[0] is False and twice[1] == []
      and m.T('The archive holds %s more than once, so nothing was taken '
              'out of it.') % "ffmpeg" in twice[4],
      "it answered %r, left %r in the tools folder, said %r"
      % (twice[0], twice[1], twice[4][-300:]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
