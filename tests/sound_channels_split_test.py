# -*- coding: utf-8 -*-
"""A file with several channels becomes several tracks.

In order: one channel cut out of four and the pair beside it, the depth
the piece is written in, the name that says which channels are in it and
keeps two pieces apart, what has to be cut at all and what does not, the
regrouping of blocks that were cut first, and last the rows the
assignment table asks for. Where a judgement rests on the material
having been built or measured, that stands as a check of its own before
it.
"""
import os
import subprocess
import sys
import tempfile
import time
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")

import importlib.util
import shutil

import numpy as np

spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


RATE = 48000
folder = tempfile.mkdtemp(prefix="vpm_split_")


def build(name, rows, depth=2):
    path = os.path.join(folder, name)
    n = min(len(r) for r in rows)
    both = np.empty(len(rows) * n)
    for i, r in enumerate(rows):
        both[i::len(rows)] = r[:n]
    with wave.open(path, "wb") as f:
        f.setnchannels(len(rows)); f.setsampwidth(depth); f.setframerate(RATE)
        top = float(2 ** (8 * depth - 1) - 1)
        f.writeframes(np.clip(both * top, -top, top)
                      .astype("<i%d" % depth).tobytes())
    return path


def tone(hz, seconds=3.0, level=0.5):
    t = np.arange(int(seconds * RATE)) / float(RATE)
    return level * np.sin(2 * np.pi * hz * t)


def peak_hz(path):
    """The loudest frequency of the first channel of a file, measured."""
    row = vpm.channel_levels(path, 8000)[0].astype(float)
    spectrum = np.abs(np.fft.rfft(row[:8000]))
    return float(np.fft.rfftfreq(8000, 1.0 / 8000)[int(np.argmax(spectrum))])


def names(paths):
    return str([os.path.basename(p) for p in paths])


print("1. Cutting one channel out")
four = build("four.wav", [tone(200), tone(400), tone(800), tone(1600)])
one = vpm.split_channels(four, (2,), os.path.join(folder, "third.wav"))
wrote = os.path.exists(one)
check("the piece is written where its name says", wrote,
      "%s, %d bytes" % (os.path.basename(one),
                        os.path.getsize(one) if wrote else 0))
got = vpm.channel_count(one) if wrote else 0
check("a piece made of one channel has one channel", got == 1,
      "1 channel wanted, %d found" % got)
top = peak_hz(one) if wrote else 0.0
check("the piece carries the channel that was asked for",
      abs(top - 800) < 12, "800 Hz wanted, %.0f Hz found" % top)

print("\n2. A pair keeps both channels")
two = vpm.split_channels(four, (0, 1), os.path.join(folder, "pair.wav"))
got = vpm.channel_count(two) if os.path.exists(two) else 0
check("a piece made of a pair has two channels", got == 2,
      "2 channels wanted, %d found" % got)

print("\n3. As deep as the original, no deeper")
check("a 16 bit recording is written back as 16 bit",
      vpm.pcm_kind(four) == "pcm_s16le",
      "pcm_s16le wanted, %s found" % vpm.pcm_kind(four))
# ffmpeg builds the material here; a failure of it says nothing about
# the program, so it stops the run outright instead of being judged.
deep = os.path.join(folder, "deep.wav")
subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                "sine=frequency=300:duration=1", "-ac", "2",
                "-c:a", "pcm_s24le", "-y", deep], check=True)
check("a 24 bit recording is written back as 24 bit",
      vpm.pcm_kind(deep) == "pcm_s24le",
      "pcm_s24le wanted, %s found" % vpm.pcm_kind(deep))
floaty = os.path.join(folder, "float.wav")
subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                "sine=frequency=300:duration=1", "-ac", "2",
                "-c:a", "pcm_f32le", "-y", floaty], check=True)
check("a float recording is written back as float",
      vpm.pcm_kind(floaty) == "pcm_f32le",
      "pcm_f32le wanted, %s found" % vpm.pcm_kind(floaty))

print("\n4. The name says which channels are in it")
for chs, wanted in (((0,), "Channel1"), ((3,), "Channel4"),
                    ((0, 1), "Channel1+2"), ((25,), "Channel26"),
                    ((26, 27), "Channel27+28")):
    name = os.path.basename(vpm.split_target("rec.wav", chs, folder))
    check("the name of a piece ends in the channels it holds",
          os.path.splitext(name)[0].endswith(wanted),
          "channels %s: %s wanted at the end, name is %s"
          % (str(chs), wanted, name))
first = vpm.split_target("rec.wav", (0,), folder)
second = vpm.split_target("rec.wav", (1,), folder)
check("two channels of one file do not land on one name",
      first != second, "%s against %s" % (os.path.basename(first),
                                          os.path.basename(second)))
here = vpm.split_target("/a/rec.wav", (0,), folder)
there = vpm.split_target("/b/rec.wav", (0,), folder)
check("two files of the same name in two folders do not land on one name",
      here != there, "%s against %s" % (os.path.basename(here),
                                        os.path.basename(there)))
pair12 = vpm.split_target("rec.wav", (0, 1), folder)
twelve = vpm.split_target("rec.wav", (11,), folder)
check("channels 1 and 2 do not land on the name of channel 12",
      pair12 != twelve, "%s against %s" % (os.path.basename(pair12),
                                           os.path.basename(twelve)))
# The name ends in a digit, which the search for continuations would read
# as a counter. It never gets that far -- the mark turns it away. The two
# pieces are really written, and into a folder of their own: without them
# on disc there is nothing the search could wrongly join, and the check
# would hold whatever the program did.
where = os.path.join(folder, "pieces")
p1 = vpm.split_channels(four, (0,), vpm.split_target(four, (0,), where))
p2 = vpm.split_channels(four, (1,), vpm.split_target(four, (1,), where))
lying = [p for p in (p1, p2) if os.path.exists(p)]
check("both pieces lie in one folder, side by side", len(lying) == 2,
      "2 files wanted, %d found: %s" % (len(lying), names(lying)))
row, _dropped = vpm.find_continuation_files(p1)
check("a piece is not taken for the next block of its recording",
      row == [p1], "1 file wanted, %d found: %s" % (len(row), names(row)))

print("\n5. What has to be cut, and what does not")
# tracks_to_split answers "nothing to do" for a file it could not read
# at all, so what was measured is asked first: otherwise a green line
# here would mean the material never arrived.
mono = vpm.channel_facts(build("mono.wav", [tone(300)]))
check("the single channel file was measured as one readable channel",
      bool(mono.get("readable")) and mono.get("channels") == 1,
      "1 readable channel wanted, %s channels and readable=%s found"
      % (mono.get("channels"), mono.get("readable")))
out = vpm.tracks_to_split("mono.wav", mono)
check("one channel alone is not cut", out == [],
      "0 tracks wanted, %d found: %s" % (len(out), str(out)))
pair = vpm.channel_facts(build("pair2.wav", [tone(300), tone(300) * 0.6]))
check("the pair file was measured as two readable channels",
      bool(pair.get("readable")) and pair.get("channels") == 2,
      "2 readable channels wanted, %s channels and readable=%s found"
      % (pair.get("channels"), pair.get("readable")))
out = vpm.tracks_to_split("pair2.wav", pair)
check("a pair the measurement keeps together is not cut", out == [],
      "0 tracks wanted, %d found: %s" % (len(out), str(out)))
out = vpm.tracks_to_split("pair2.wav", pair, {0: False})
check("the same pair, taken apart by hand, gives two tracks",
      len(out) == 2, "2 tracks wanted, %d found: %s" % (len(out), str(out)))
half = vpm.channel_facts(build("half.wav", [tone(300),
                                            np.zeros(3 * RATE)]))
check("the empty channel of the half file was measured as empty",
      list(half.get("silent") or []) == [False, True],
      "[False, True] wanted, %s found" % str(half.get("silent")))
out = vpm.tracks_to_split("half.wav", half)
check("an empty channel is dropped and the other one kept",
      len(out) == 1 and out[0][0] == (0,),
      "1 track of channel 1 wanted, %d found: %s" % (len(out), str(out)))

print("\n6. Blocks are cut first, then regrouped")
# The pieces carry the names split_target builds, not names made up here:
# the regrouping reads the channel out of the name, and a test that
# invents its own name would keep passing after the name changed.
a1 = [vpm.split_target("a1.wav", (0,), "/out"),
      vpm.split_target("a1.wav", (1,), "/out")]
a2 = [vpm.split_target("a2.wav", (0,), "/out"),
      vpm.split_target("a2.wav", (1,), "/out")]
# Two pieces again, but cut along a different seam: the pair together
# and the third channel on its own.
a3 = [vpm.split_target("a3.wav", (0, 1), "/out"),
      vpm.split_target("a3.wav", (2,), "/out")]


def split_of(p):
    return {"a1.wav": a1, "a2.wav": a2, "a3.wav": a3, "b1.wav": []}.get(
        os.path.basename(p), [])


rows = vpm.expand_chains_to_tracks(
    [(["a1.wav", "a2.wav"], [("x", "why")]), (["b1.wav"], [])], split_of)
check("two blocks of two channels give two tracks, the uncut file a third",
      len(rows) == 3, "3 rows wanted, %d found: %s" % (len(rows), str(rows)))
check("each track keeps both its blocks",
      len(rows) >= 2 and rows[0][0] == [a1[0], a2[0]]
      and rows[1][0] == [a1[1], a2[1]],
      "%s and %s wanted, %s found"
      % (names([a1[0], a2[0]]), names([a1[1], a2[1]]),
         str([names(r[0]) for r in rows[:2]])))
check("what could not be cut stays as it was",
      len(rows) >= 3 and rows[2][0] == ["b1.wav"],
      "['b1.wav'] wanted, %s found"
      % (names(rows[2][0]) if len(rows) >= 3 else "no third row"))
check("the discarded blocks are named once, not per track",
      len(rows) >= 2 and bool(rows[0][1]) and not rows[1][1],
      "1 named and 0 wanted, %s found" % str([len(r[1]) for r in rows]))

uneven = vpm.expand_chains_to_tracks([(["a1.wav", "b1.wav"], [])], split_of)
check("blocks that did not all come apart stay whole",
      len(uneven) == 1 and uneven[0][0] == ["a1.wav", "b1.wav"],
      "1 row of 2 files wanted, %d rows found: %s"
      % (len(uneven), str([names(r[0]) for r in uneven])))
seams = vpm.expand_chains_to_tracks([(["a1.wav", "a3.wav"], [])], split_of)
check("blocks cut along different seams stay whole",
      len(seams) == 1 and seams[0][0] == ["a1.wav", "a3.wav"],
      "1 row of 2 files wanted, %d rows found: %s"
      % (len(seams), str([names(r[0]) for r in seams])))

print("\n7. The assignment table asks for the tracks")
# Two files that are not blocks of one another: two recordings, each
# with two channels, so four tracks.
chains, camera, _own = vpm.assignment_rows(
    ["a1.wav", "a2.wav"], [], (), split_of)
check("two recordings of two channels become four tracks",
      len(chains) == 4, "4 rows wanted, %d found" % len(chains))
check("and each channel is a row of its own, in the order they were cut",
      [c[0][0] for c in chains] == [a1[0], a1[1], a2[0], a2[1]],
      "%s wanted, %s found" % (names([a1[0], a1[1], a2[0], a2[1]]),
                               names([c[0][0] for c in chains])))
check("no camera audio is put in the way", camera is False,
      "False wanted, %s found" % str(camera))
plain, _c, _o = vpm.assignment_rows(["a1.wav", "a2.wav"], [])
check("without a splitter the two recordings stay two rows",
      len(plain) == 2, "2 rows wanted, %d found" % len(plain))
uncut = vpm.assignment_rows(["b1.wav"], [], (), split_of)[0]
check("a recording that cannot be cut stays one row", len(uncut) == 1,
      "1 row wanted, %d found: %s" % (len(uncut), str(uncut)))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
