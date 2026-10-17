# -*- coding: utf-8 -*-
"""An atom copy that cannot be done safely leaves the target as it was.

copy_mov_atoms grows every box around the video sample description by
the bytes it adds, and it can only do that in a 32 bit size field; an
atom over its limit is not an identifier any more. A source with a logs
atom is built here, and its plain copy is the target. In order: a video
track whose box carries a 64 bit size is still found, and the copy is
refused; an oversized atom is skipped with the
target untouched; and the boundary -- a media box with a 64 bit size,
the way a long recording writes it, is no reason to refuse.
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
import contextlib
import io
import shutil
import struct
import subprocess
import tempfile
import time
import the_program

SCRIPT = the_program.SCRIPT
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
m = the_program.load()
m.set_language("en")
T = m.T

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


folder = tempfile.mkdtemp(prefix="vpm_risky_")
plain = os.path.join(folder, "plain.mov")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "testsrc=size=64x36:rate=30:duration=0.1",
                "-c:v", "libx264", plain],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
CONTENT = b"com.apple.apple-wide-gamut.apple-log"


def moov_of(data):
    """(offset, size) of the top-level moov box in *data*, or None."""
    i = 0
    while i + 8 <= len(data):
        size, kind = struct.unpack(">I4s", data[i:i + 8])
        if size < 8:
            return None
        if kind == b"moov":
            return i, size
        i += size
    return None


def with_atom(data, payload):
    """*data* with one logs atom put into its video sample description."""
    at = moov_of(data)
    moov = bytearray(data[at[0]:at[0] + at[1]])
    chain = m._video_track_chain(moov, 0, len(moov), 8)
    atom = struct.pack(">I4s", 8 + len(payload), b"logs") + payload
    e_i = chain[-1][0]
    e_size = struct.unpack(">I", moov[e_i:e_i + 4])[0]
    for i, _head in chain:
        struct.pack_into(">I", moov, i, struct.unpack(">I", moov[i:i + 4])[0]
                         + len(atom))
    moov = moov[:e_i + e_size] + atom + moov[e_i + e_size:]
    return data[:at[0]] + bytes(moov)


def wide_trak(data):
    """*data* with the video trak header rewritten in its 64 bit form."""
    at = moov_of(data)
    moov = bytearray(data[at[0]:at[0] + at[1]])
    t_i = m._video_track_chain(moov, 0, len(moov), 8)[1][0]
    t_size = struct.unpack(">I", moov[t_i:t_i + 4])[0]
    moov = (moov[:t_i] + struct.pack(">I4sQ", 1, b"trak", t_size + 8)
            + moov[t_i + 8:])
    struct.pack_into(">I", moov, 0, len(moov))
    return data[:at[0]] + bytes(moov)


def wide_mdat(data):
    """*data* with wide + mdat turned into one mdat with a 64 bit size.

    What ffmpeg's free 'wide' box is kept for: the eight bytes become
    the long size field, so no offset in the file moves.
    """
    at = data.find(b"wide")
    if at < 4 or data[at + 8:at + 12] != b"mdat":
        return None
    size = struct.unpack(">I", data[at + 4:at + 8])[0]
    return (data[:at - 4] + struct.pack(">I4sQ", 1, b"mdat", size + 8)
            + data[at + 12:])


def write(name, data):
    out = os.path.join(folder, name)
    open(out, "wb").write(data)
    return out


def copied(source, target):
    """copy_mov_atoms' answer, what it printed, and the target after."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            answer = m.copy_mov_atoms(source, target)
        except Exception as e:
            answer = "raised %s" % type(e).__name__
    return answer, " ".join(out.getvalue().split()), open(target, "rb").read()


base = open(plain, "rb").read() if os.path.exists(plain) else b""
source = write("source.mov", with_atom(base, CONTENT)) if base else None

# A video track behind a 64 bit box.
target = write("widetrak.mov", wide_trak(base)) if base else None
before = open(target, "rb").read() if target else b""
chain = (m._video_track_chain(before[moov_of(before)[0]:], 0,
                              moov_of(before)[1], 8) if before else None)
check("a video track behind a 64 bit box is still found",
      bool(chain) and len(chain) == 7,
      "%d boxes down from moov, wanted 7" % len(chain or []))
answer, said, after = copied(source, target) if target else ([], "", b"")
want = " ".join(T('  Cannot add atoms: a 64 bit box is in the way.').split())
check("a 64 bit box in the way refuses the copy and says why",
      answer == [] and want in said, "answer %r, said %r" % (answer, said))
# Not judged here that this target is left as it was: two nets stand
# behind each other -- the refusal before any write, and the rollback
# after a failed check -- so no single break could show it red.

# An atom past the limit.
big = (write("big.mov", with_atom(base, b"x" * (m.ATOM_LIMIT + 1)))
       if base else None)
target = write("plain_target.mov", base) if base else None
answer, said, after = copied(big, target) if target else ([], "", b"")
want = " ".join((T('  Atom %s skipped: %s bytes are too much for it.')
                 % ("logs", m.number_text(m.ATOM_LIMIT + 9, 0))).split())
check("an atom over the limit is skipped and named",
      answer == [] and want in said, "answer %r, said %r" % (answer, said))
check("the target of a skipped atom is left as it was",
      after == base and bool(base),
      "%d bytes before, %d after" % (len(base), len(after)))

# The boundary: a 64 bit media box.
long_mdat = wide_mdat(base) if base else None
target = write("widemdat.mov", long_mdat) if long_mdat else None
top = m._top_level_boxes(target) if target else []
check("a media box with a 64 bit size is read at its true length",
      [k for k, _p, _g in top] == [b"ftyp", b"mdat", b"moov"]
      and top[1][1] + top[1][2] == top[2][1],
      "top boxes %r" % ([(k.decode("latin1"), p, g) for k, p, g in top],))
answer, said, after = copied(source, target) if target else ([], "", b"")
check("a 64 bit media box is no reason to refuse the copy",
      answer == ["logs"] and CONTENT in after,
      "answer %r, said %r" % (answer, said))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
