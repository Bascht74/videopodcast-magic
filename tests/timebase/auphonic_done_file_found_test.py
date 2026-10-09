# -*- coding: utf-8 -*-
"""--auphonic-done takes a file by its name and length, or says why not.

processed_tracks_taken in this process, over folders of WAV files made
here: silence, with one loud stretch where the window begins. Sections:
a file named after its track and as long as the window is taken whole;
one as long as the measured range without In and Out point is trimmed
to the window, its loud stretch landing on the margin, and a jingle in
front moves the trim by the jingle's length; a file of another length,
or none with a fitting name, is refused and named; and --without-auphonic
beside it is said to lose. The trim is read back out of the file ffmpeg
wrote, by where its first sound lies.
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
import re
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


RATE = 48000
ROOM = tempfile.mkdtemp(prefix="vpm_done_found_")
# The window is 5 s; the measured range without In and Out point 70 s,
# and the window begins 4 s into it. Lengths more than a minute apart,
# so a file of the one is never taken for the other.
WINDOW, WHOLE, SHIFT = 5.0, 70.0, 4.0
MARGIN = 30.0          # the slack the program leaves at each end


def wav(folder, name, seconds, loud_at=None):
    """A mono 16-bit WAV of silence, loud for 0.1 s from *loud_at*."""
    os.makedirs(folder, exist_ok=True)
    frames = bytearray(int(seconds * RATE) * 2)
    if loud_at is not None:
        start = int(loud_at * RATE) * 2
        frames[start:start + int(0.1 * RATE) * 2] = b"\x00\x40" * int(
            0.1 * RATE)
    path = os.path.join(folder, name)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(bytes(frames))
    return path


def first_sound(path):
    """Seconds into *path* where its first non-silent sample lies, or None."""
    with wave.open(path, "rb") as w:
        width, channels = w.getsampwidth(), w.getnchannels()
        data = w.readframes(w.getnframes())
    hit = re.search(b"[^\x00]", data)
    if hit is None:
        return None
    return hit.start() // (width * channels) / float(RATE)


def take(folder, names, lengths, measured=None, shift=0.0,
         without=False):
    """processed_tracks_taken over *folder*: (answer, tracks, said)."""
    args = types.SimpleNamespace(auphonic_done=folder,
                                 without_auphonic=without)
    tracks = [{"name": n} for n in names]
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        answer = vpm.processed_tracks_taken(
            args, tracks, tempfile.mkdtemp(dir=ROOM), lengths, measured,
            shift)
    return answer, tracks, said.getvalue()


print("1. Taken whole")
folder = os.path.join(ROOM, "whole")
guest = wav(folder, "Guest.wav", WINDOW)
host = wav(folder, "Presenter_auphonic.wav", WINDOW)
answer, tracks, said = take(folder, ["Guest", "Presenter"],
                            {"Guest": WINDOW, "Presenter": WINDOW})
check("each track takes the file named after it, as long as the window",
      answer is True and [t.get("done") for t in tracks] == [guest, host],
      "answered %r, took %r" % (answer, [t.get("done") and os.path.basename(
          t["done"]) for t in tracks]))

print("\n2. Trimmed from the measured range")
folder = os.path.join(ROOM, "range")
wav(folder, "Guest.wav", WHOLE, loud_at=SHIFT)
answer, tracks, said = take(folder, ["Guest"], {"Guest": WINDOW},
                            measured=WHOLE, shift=SHIFT)
got = tracks[0].get("done")
heard = first_sound(got) if got and os.path.isfile(got) else None
check("a file as long as the measured range is trimmed to the window",
      answer is True and tracks[0].get("edge") == MARGIN and heard is not None,
      "answered %r, edge %r, wrote %r" % (answer, tracks[0].get("edge"),
                                          got and os.path.basename(got)))
check("and the window's beginning lands on the margin",
      heard is not None and abs(heard - MARGIN) < 0.01,
      "first sound at %s s, wanted %.2f" % (heard, MARGIN))

JINGLE = 3.0
folder = os.path.join(ROOM, "jingle")
wav(folder, "Guest.wav", WHOLE + JINGLE, loud_at=SHIFT + JINGLE)
answer, tracks, said = take(folder, ["Guest"], {"Guest": WINDOW},
                            measured=WHOLE, shift=SHIFT)
got = tracks[0].get("done")
heard = first_sound(got) if got and os.path.isfile(got) else None
check("a jingle in front moves the trim by its own length",
      answer is True and heard is not None and abs(heard - MARGIN) < 0.01,
      "answered %r, first sound at %s s, wanted %.2f"
      % (answer, heard, MARGIN))

print("\n3. Refused")
folder = os.path.join(ROOM, "other")
wav(folder, "Guest.wav", WHOLE)
answer, tracks, said = take(folder, ["Guest"], {"Guest": WINDOW})
other = vpm.T('    %-20s <- %s  BUT %s -- neither the time window '
              '(%s) nor the\n    %-20s    whole measured range (%s). '
              'This belongs to another run.') % (
    "Guest", "Guest.wav", vpm.as_hms(WHOLE), vpm.as_hms(WINDOW), "",
    vpm.as_hms(WINDOW))
check("a file of neither length is refused as another run's",
      answer is False and not tracks[0].get("done") and other in said,
      "answered %r, took %r, the refusal said: %s"
      % (answer, tracks[0].get("done") and os.path.basename(
          tracks[0]["done"]), other in said))
folder = os.path.join(ROOM, "unnamed")
wav(folder, "Guest.wav", WINDOW)
answer, tracks, said = take(folder, ["Interviewer"],
                            {"Interviewer": WINDOW})
named = vpm.T('    %-20s no file with a matching name') % "Interviewer"
check("a track with no file of a fitting name is refused and named",
      answer is False and not tracks[0].get("done") and named in said,
      "answered %r, took %r, %r said: %s"
      % (answer, tracks[0].get("done") and os.path.basename(
          tracks[0]["done"]), named.strip(), named in said))

print("\n4. Beside --without-auphonic")
folder = os.path.join(ROOM, "whole")
answer, tracks, said = take(folder, ["Guest"], {"Guest": WINDOW},
                            without=True)
lose = vpm.T('  --without-auphonic and --auphonic-done were both given. '
             'The finished tracks win: there is nothing left to send '
             'anywhere.')
check("--without-auphonic beside it is said to lose to the files",
      lose in said and answer is True,
      "answered %r, the warning said: %s" % (answer, lose in said))

shutil.rmtree(ROOM, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
