# -*- coding: utf-8 -*-
"""An audio-only join writes nothing dry, and takes finished tracks or ends.

join_only in this process, for recordings with no picture, over WAV
files made here; the loudness measurement and the return check are
replaced where the piece looks them up. Sections: a loudness that
cannot be measured is said and the join goes on; a dry run names the
joined file it would write and writes nothing; and with --auphonic-done
a folder with no fitting file ends the join with 1, while a fitting one
is taken on a dry run without the return check.
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
import tempfile
import time
import types
import wave
import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-62s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


ROOM = tempfile.mkdtemp(prefix="vpm_join_done_")
WORK = os.path.join(ROOM, "out")
os.makedirs(WORK)
WHY = "stand-in: no loudness here"


def wav(folder, name, seconds=2.0):
    """A mono 16-bit WAV of silence at 48 kHz."""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(b"\x00\x00" * int(48000 * seconds))
    return path


SOURCE = wav(os.path.join(ROOM, "material"), "Rec_joined_source.wav")
BLOCKS = [os.path.join(ROOM, "material", "Rec_001.wav"),
          os.path.join(ROOM, "material", "Rec_002.wav")]


def unmeasurable(*a, **k):
    raise ValueError(WHY)


verified = []
vpm.normalise_loudness = unmeasurable
vpm.verify_returned_tracks = (lambda tracks, window, tmpdir:
                              verified.append(window) or True)


def join(finished=None):
    """join_only, dry, for one recording of two blocks: (returned, said)."""
    del verified[:]
    args = types.SimpleNamespace(
        out=WORK, lufs=-16.0, auphonic_key=None, auphonic_done=finished,
        dry_run=True, in_point=None, out_point=None, without_auphonic=False)
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        got = vpm.join_only(args, [{"name": "Guest", "source": SOURCE,
                                    "blocks": list(BLOCKS)}],
                            tempfile.mkdtemp(dir=ROOM))
    return got, said.getvalue()


print("1. Joined dry")
got, said = join()
unmeasured = vpm.T('  Loudness not measurable: %s') % WHY
check("a loudness that cannot be measured is said, and the join goes on",
      unmeasured in said and got == 0,
      "%r said: %s; returned %r" % (unmeasured.strip(), unmeasured in said,
                                    got))
would = vpm.T('Would write: %s') % os.path.join(WORK, "Rec_joined.wav")
check("a dry run names the joined file it would write",
      would in said, "'Would write: .../Rec_joined.wav' said: %s"
      % (would in said))
check("and writes nothing", os.listdir(WORK) == [],
      "written: %r" % os.listdir(WORK))

print("\n2. With finished tracks")
got, said = join(os.path.dirname(wav(os.path.join(ROOM, "none"),
                                     "Other.wav")))
check("a folder with no fitting finished file ends the join with 1",
      got == 1 and not verified,
      "returned %r, wanted 1; the return check ran %d times"
      % (got, len(verified)))
got, said = join(os.path.dirname(wav(os.path.join(ROOM, "fits"),
                                     "Guest.wav")))
check("a fitting one is taken dry without the return check",
      got == 0 and not verified,
      "returned %r, wanted 0; the return check ran %d times"
      % (got, len(verified)))

shutil.rmtree(ROOM, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
