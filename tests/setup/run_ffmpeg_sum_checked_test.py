# -*- coding: utf-8 -*-
"""A fetched ffmpeg build is unpacked only when the release's sum fits it.

The build comes off a moving tag somebody else fills, and before this
was held against anything a stand-in whose ffmpeg was a shell script
was reported as a success. The release lists a SHA-256 for every
archive in it, so the fetch asks that list and unpacks nothing it does
not match. The cases in order: the sum fits, and the two programs
arrive; the sum differs, the list cannot be had, the list does not name
the archive, or the archive holds ffmpeg twice -- and in each of those
nothing lands in the tools folder, the archive is gone again, and the
reason is said. The one function that opens a connection is replaced
and the sockets are shut besides, so nothing here goes outside.
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
# The address is asked of the program for the machine run() pretends
# to be, not written here: it moves with every ffmpeg line. What this
# test holds fixed is the list's name beside it, which BtbN chose.
was_machine = (m.sys.platform, m.platform.machine)
try:
    m.sys.platform, m.platform.machine = "linux", (lambda: "x86_64")
    URL = m.ffmpeg_build_url()
finally:
    m.sys.platform, m.platform.machine = was_machine
PLACE, ARCHIVE = URL.rsplit("/", 1)
SUMS = PLACE + "/checksums.sha256"


def listing(sums):
    """A checksum list in the shape sha256sum writes, as BtbN's is."""
    return "".join("%s  %s\n" % (s, n) for n, s in sums).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def outside(address):
    raise OSError("the test shut the network: %r" % (address,))


def run(served):
    """fetch_ffmpeg_build on a Linux machine against that stand-in release.

    *served* maps an address to the bytes it answers with; any other
    address answers like a missing file. Returns what it answered, what
    lay in the tools folder afterwards, whether a fetched file was left
    on disk, the addresses asked, and everything it said.
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
           m.tools_folder, m.open_page, socket.socket.connect,
           socket.create_connection)
    try:
        m.sys.platform, m.platform.machine = "linux", (lambda: "x86_64")
        m.fetch_archive = fetch
        m.tools_folder = lambda make=False: room
        m.open_page = lambda url: False
        socket.socket.connect = lambda one, address, *rest: outside(address)
        socket.create_connection = lambda address, *rest, **more: \
            outside(address)
        answer = m.fetch_ffmpeg_build(asked=True, say=said.append)
    finally:
        (silent, path, m.sys.platform, m.platform.machine, m.fetch_archive,
         m.tools_folder, m.open_page, socket.socket.connect,
         socket.create_connection) = was
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
    url, sums = URL, SUMS
    OTHER = "ffmpeg-n9.0-latest-win64-gpl-9.0.zip"
    fits = run({url: GOOD,
                sums: listing([(OTHER, sha(b"x")), (ARCHIVE, sha(GOOD))])})
    wrong = run({url: GOOD, sums: listing([(ARCHIVE, sha(b"other"))])})
    no_list = run({url: GOOD})
    unnamed = run({url: GOOD, sums: listing([(OTHER, sha(GOOD))])})
    twice = run({url: TWICE, sums: listing([(ARCHIVE, sha(TWICE))])})
finally:
    shutil.rmtree(WORK, ignore_errors=True)

print("1. A build whose sum fits is unpacked")
check("a build whose listed sum fits is unpacked and reported",
      fits[0] is True and fits[1] == ["ffmpeg", "ffprobe"],
      "it answered %r and left %r in the tools folder, wanted True and "
      "ffmpeg, ffprobe -- asked %r, said %r"
      % (fits[0], fits[1], fits[3], fits[4][-200:]))

print("\n2. A build that does not fit is refused, and says why")
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
check("a build is refused when the list of sums cannot be had",
      no_list[0] is False and no_list[1] == []
      and m.T('The list of checksums could not be fetched, so the build '
              'was not unpacked: %s')
      % "HTTP Error 404: Not Found (the test's stand-in)" in no_list[4],
      "it answered %r, left %r in the tools folder, said %r"
      % (no_list[0], no_list[1], no_list[4][-300:]))
check("a build is refused when the list does not name its archive",
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
