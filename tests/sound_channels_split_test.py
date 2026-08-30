# -*- coding: utf-8 -*-
"""A file with several channels becomes several tracks."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, shutil, sys, tempfile, wave
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

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


print("1. Cutting one channel out")
four = build("four.wav", [tone(200), tone(400), tone(800), tone(1600)])
one = vpm.split_channels(four, (2,), os.path.join(folder, "third.wav"))
check("the file is written", os.path.exists(one))
check("and it has one channel", vpm.channel_count(one) == 1,
      vpm.channel_count(one))
back = vpm.channel_levels(one, 8000)[0].astype(float)
spectrum = np.abs(np.fft.rfft(back[:8000]))
top = float(np.fft.rfftfreq(8000, 1.0 / 8000)[int(np.argmax(spectrum))])
check("and it is the third channel, not another", abs(top - 800) < 12, top)

print("\n2. A pair keeps both channels")
two = vpm.split_channels(four, (0, 1), os.path.join(folder, "pair.wav"))
check("two channels come out", vpm.channel_count(two) == 2,
      vpm.channel_count(two))

print("\n3. As deep as the original, no deeper")
check("16 bit stays 16 bit", vpm.pcm_kind(four) == "pcm_s16le",
      vpm.pcm_kind(four))
import subprocess
deep = os.path.join(folder, "deep.wav")
subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                "sine=frequency=300:duration=1", "-ac", "2",
                "-c:a", "pcm_s24le", "-y", deep], check=True)
check("24 bit stays 24 bit", vpm.pcm_kind(deep) == "pcm_s24le",
      vpm.pcm_kind(deep))
floaty = os.path.join(folder, "float.wav")
subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                "sine=frequency=300:duration=1", "-ac", "2",
                "-c:a", "pcm_f32le", "-y", floaty], check=True)
check("float stays float", vpm.pcm_kind(floaty) == "pcm_f32le",
      vpm.pcm_kind(floaty))

print("\n4. The name says which channels are in it")
for chs, wanted in (((0,), "Channel1"), ((3,), "Channel4"),
                    ((0, 1), "Channel1+2"), ((25,), "Channel26"),
                    ((26, 27), "Channel27+28")):
    name = os.path.basename(vpm.split_target("rec.wav", chs, folder))
    check("%-9s -> %s" % (str(chs), name),
          os.path.splitext(name)[0].endswith(wanted), name)
check("and two tracks do not collide",
      vpm.split_target("rec.wav", (0,), folder)
      != vpm.split_target("rec.wav", (1,), folder))
check("nor do two files of the same name in two folders",
      vpm.split_target("/a/rec.wav", (0,), folder)
      != vpm.split_target("/b/rec.wav", (0,), folder))
check("nor channels 1 and 2 with channel 12",
      vpm.split_target("rec.wav", (0, 1), folder)
      != vpm.split_target("rec.wav", (11,), folder))
# The name ends in a digit, which the search for continuations would read
# as a counter. It never gets that far -- the mark turns it away.
piece = vpm.split_target("rec.wav", (0,), folder)
check("a piece is not taken for a continuation block",
      vpm.find_continuation_files(piece)[0] == [piece],
      str(vpm.find_continuation_files(piece)[0]))

print("\n5. What has to be cut, and what does not")
mono = vpm.channel_facts(build("mono.wav", [tone(300)]))
check("one channel: nothing to do",
      vpm.tracks_to_split("mono.wav", mono) == [], "")
pair = vpm.channel_facts(build("pair2.wav", [tone(300), tone(300) * 0.6]))
check("a pair that stays together: nothing to do",
      vpm.tracks_to_split("pair2.wav", pair) == [],
      str(vpm.tracks_to_split("pair2.wav", pair)))
check("the same pair, taken apart by hand: two tracks",
      len(vpm.tracks_to_split("pair2.wav", pair, {0: False})) == 2,
      str(vpm.tracks_to_split("pair2.wav", pair, {0: False})))
half = vpm.channel_facts(build("half.wav", [tone(300),
                                            np.zeros(3 * RATE)]))
out = vpm.tracks_to_split("half.wav", half)
check("an empty channel is dropped, the other kept",
      len(out) == 1 and out[0][0] == (0,), str(out))

print("\n6. Blocks are cut first, then regrouped")
# The pieces carry the names split_target builds, not names made up here:
# the regrouping reads the channel out of the name, and a test that
# invents its own name would keep passing after the name changed.
a1 = [vpm.split_target("a1.wav", (0,), "/out"),
      vpm.split_target("a1.wav", (1,), "/out")]
a2 = [vpm.split_target("a2.wav", (0,), "/out"),
      vpm.split_target("a2.wav", (1,), "/out")]


def split_of(p):
    return {"a1.wav": a1, "a2.wav": a2, "b1.wav": []}.get(
        os.path.basename(p), [])

rows = vpm.expand_chains_to_tracks(
    [(["a1.wav", "a2.wav"], [("x", "why")]), (["b1.wav"], [])], split_of)
check("a recording of two blocks with two channels: two tracks",
      len(rows) == 3, str(len(rows)))
check("each track keeps both its blocks",
      rows[0][0] == [a1[0], a2[0]] and rows[1][0] == [a1[1], a2[1]],
      str(rows[:2]))
check("what could not be cut stays as it was",
      rows[2][0] == ["b1.wav"], str(rows[2]))
check("the discarded blocks are named once, not per track",
      rows[0][1] and not rows[1][1], str([r[1] for r in rows]))

uneven = vpm.expand_chains_to_tracks(
    [(["a1.wav", "b1.wav"], [])], split_of)
check("blocks that came apart differently stay whole",
      uneven[0][0] == ["a1.wav", "b1.wav"], str(uneven))

print("\n7. The assignment table asks for the tracks")
# Two files that are not blocks of one another: two recordings, each
# with two channels, so four tracks.
chains, camera, _own = vpm.assignment_rows(
    ["a1.wav", "a2.wav"], [], (), split_of)
check("two recordings of two channels become four tracks",
      len(chains) == 4, str(len(chains)))
check("and each is a track of its own",
      [c[0][0] for c in chains] == [a1[0], a1[1], a2[0], a2[1]],
      str([c[0][0] for c in chains]))
check("no camera audio in the way", camera is False)
chains, _c, _o = vpm.assignment_rows(["a1.wav", "a2.wav"], [])
check("without the splitter they stay two recordings", len(chains) == 2,
      str(len(chains)))
check("one that cannot be cut stays one row",
      len(vpm.assignment_rows(["b1.wav"], [], (), split_of)[0]) == 1)

shutil.rmtree(folder, ignore_errors=True)
print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
