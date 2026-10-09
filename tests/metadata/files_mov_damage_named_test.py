# -*- coding: utf-8 -*-
"""A MOV file damaged by an atom edit is named, never taken for whole.

_verify_mov_after_edit is what copy_mov_atoms asks after writing, and
an answer that is not empty makes it put the old moov back. A short clip
is written here, and copies of it are damaged byte by byte the ways a
write can go wrong. In order: the material and the sound file passing,
then a top box too short to read, a box behind moov, a file cut short,
the media data moved, a moov that has not grown, a file with no video
track, an atom that did not arrive, and a file that is not there.
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


folder = tempfile.mkdtemp(prefix="vpm_movdamage_")
clip = os.path.join(folder, "clip.mov")
sound = os.path.join(folder, "sound.mov")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "testsrc=size=64x36:rate=30:duration=0.1",
                "-c:v", "libx264", clip],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "sine=frequency=440:duration=0.1", "-c:a", "pcm_s16le",
                sound], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

top = m._top_level_boxes(clip) if os.path.exists(clip) else []
check("the clip ends in moov, the way the program edits it",
      bool(top) and top[-1][0] == b"moov",
      "top boxes %s" % ", ".join("%s@%d" % (k.decode("latin1"), p)
                                 for k, p, _g in top))
pos, size = (top[-1][1], top[-1][2]) if top else (0, 0)
whole = open(clip, "rb").read() if os.path.exists(clip) else b""


def variant(name, data):
    out = os.path.join(folder, name)
    open(out, "wb").write(data)
    return out


def verdict(path, old_size=None, before=None, for_it=()):
    """The answer for *path* against the clip's state before the edit.

    The moov counts as grown by one byte unless *old_size* says other.
    """
    try:
        return m._verify_mov_after_edit(
            path, pos, size - 1 if old_size is None else old_size,
            top if before is None else before, list(for_it))
    except Exception as e:
        return "raised %s" % type(e).__name__


got = verdict(clip)
check("the clip as written passes", got == "", "answer %r" % got)

short_head = bytearray(whole)
struct.pack_into(">I", short_head, 0, 4)
got = verdict(variant("short.mov", bytes(short_head)))
want = T('boxes no longer readable')
check("a top box too short to read is named", got == want,
      "%r, wanted %r" % (got, want))

# Sixteen bytes, not eight: an empty box flush with the end is not
# read as a box at all (the loop stops eight bytes short of the end).
behind = whole + struct.pack(">I4s", 16, b"free") + b"\0" * 8
got = verdict(variant("behind.mov", behind))
want = T('moov is no longer in its place')
check("a box written behind moov is named", got == want,
      "%r, wanted %r" % (got, want))

got = verdict(variant("cut.mov", whole[:-10]))
want = T('moov no longer ends at the end of the file')
check("a file cut short at the end is named", got == want,
      "%r, wanted %r" % (got, want))

moved = [(k, p + 8 if k == b"mdat" else p, g) for k, p, g in top]
got = verdict(clip, before=moved)
want = T('the media data is no longer where it was')
check("media data that moved is named", got == want,
      "%r, wanted %r" % (got, want))

got = verdict(clip, old_size=size)
want = T('moov has not grown')
check("a moov that has not grown is named", got == want,
      "%r, wanted %r" % (got, want))

stop = m._top_level_boxes(sound) if os.path.exists(sound) else []
got = (m._verify_mov_after_edit(sound, stop[-1][1], stop[-1][2] - 1, stop,
                                [])
       if stop else "no sound file")
want = T('the video track can no longer be found')
check("a file without a video track is named", got == want,
      "%r, wanted %r" % (got, want))

got = verdict(clip, for_it=[b"logs"])
want = T('did not arrive: %s') % "logs"
check("an atom that did not arrive is named", got == want,
      "%r, wanted %r" % (got, want))

got = verdict(os.path.join(folder, "gone.mov"))
want = T('cannot be read back (%s)').split("(")[0]
check("a file that is not there is named, not raised",
      got.startswith(want) and got != want,
      "%r, wanted it to begin %r" % (got, want))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
