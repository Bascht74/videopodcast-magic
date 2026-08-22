# -*- coding: utf-8 -*-
"""Six defects an adversarial review turned up, each nailed down here.

They share nothing but their origin, so the file is grouped by defect
rather than by subject. Each block says what went wrong before, because
that is what the check is guarding.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, struct, subprocess, sys, tempfile, wave
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="reviewfix_")
bad = []


def check(what, ok, detail=""):
    print("  %-58s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


def facts(channels, level, pair_zero, pair_same=None, pair_apart=None):
    """A measured block, as channel_facts hands it out."""
    n = len(level)
    return {"channels": channels, "level": list(level),
            "silent": [False] * n, "readable": True,
            "pair_zero": list(pair_zero),
            "pair_same": list(pair_same or [0.0] * (n - 1)),
            "pair_apart": list(pair_apart or [0.0] * (n - 1))}


print("1. blocks_facts keeps the answer of the loudest block")
# The inner loop reused the name of the list it was filling, so from the
# first measured pair on, the answers were appended to that block's own
# list -- and the block that was loudest was thrown away.
show = facts(2, [-6.0, -6.0], [0.90])
runout = facts(2, [-40.0, -40.0], [0.10])
out = vpm.blocks_facts_from([show, runout])
check("two blocks, one answer per pair", len(out["pair_zero"]) == 1,
      str(out["pair_zero"]))
check("and it is the loudest block's", abs(out["pair_zero"][0] - 0.90) < 1e-9,
      str(out["pair_zero"]))
other_way = vpm.blocks_facts_from([runout, show])
check("the order of the blocks does not decide",
      other_way["pair_zero"] == out["pair_zero"],
      "%s vs %s" % (other_way["pair_zero"], out["pair_zero"]))
check("and the block it read is left as it was",
      show["pair_zero"] == [0.90] and runout["pair_zero"] == [0.10],
      "%s %s" % (show["pair_zero"], runout["pair_zero"]))
four_show = facts(4, [-6.0] * 4, [0.95, 0.08, 0.93])
four_quiet = facts(4, [-90.0] * 4, [None, None, None])
out4 = vpm.blocks_facts_from([four_show, four_quiet])
check("a block of pure silence does not erase the show",
      out4["pair_zero"] == [0.95, 0.08, 0.93], str(out4["pair_zero"]))

print("\n2. Split pieces are recognised by the name they carry today")
# which() looked for "_ch", the name from before 0.4.0. The pieces are
# called "_Channel1" now, so nothing matched, the whole stem was compared,
# and a recording of several blocks never came apart into tracks.
one = vpm.split_target("/card1/REC0001.WAV", (0,), "/out")
two = vpm.split_target("/card1/REC0002.WAV", (0,), "/out")
pair1 = vpm.split_target("/card1/REC0001.WAV", (1, 2), "/out")
pair2 = vpm.split_target("/card1/REC0002.WAV", (1, 2), "/out")
pieces = {"/card1/REC0001.WAV": [one, pair1],
          "/card1/REC0002.WAV": [two, pair2]}
rows = vpm.expand_chains_to_tracks(
    [(["/card1/REC0001.WAV", "/card1/REC0002.WAV"], [])],
    lambda x: pieces.get(x) or [])
check("two blocks, two channels -> two recordings", len(rows) == 2,
      str(len(rows)))
check("each holding both blocks",
      all(len(r) == 2 for r, _d in rows), str([len(r) for r, _d in rows]))
check("channel 1 with channel 1",
      [os.path.basename(x) for x in rows[0][0]]
      == [os.path.basename(one), os.path.basename(two)],
      str([os.path.basename(x) for x in rows[0][0]]))
mixed = {"/card1/REC0001.WAV": [one, pair1],
         "/card1/REC0002.WAV": [two]}
check("blocks that came apart differently stay whole",
      len(vpm.expand_chains_to_tracks(
          [(["/card1/REC0001.WAV", "/card1/REC0002.WAV"], [])],
          lambda x: mixed.get(x) or [])) == 1)

print("\n3. Blocks are joined in the order they were handed over")
RATE = 48000


def tone(name, hz, seconds=1.0):
    path = os.path.join(WORK, name)
    t = np.arange(int(seconds * RATE)) / float(RATE)
    x = (0.5 * np.sin(2 * np.pi * hz * t) * 32767).astype("<i2")
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(x.tobytes())
    return path


first = tone("zz_first.wav", 440.0)
second = tone("aa_second.wav", 1500.0)
target = os.path.join(WORK, "joined.wav")
vpm.join_audio_parts([first, second], target)


def loudest_hz(path, from_s, to_s):
    """The strongest frequency in this stretch, read through ffmpeg.

    The joined file is 24 bit and extensible, which the wave module of
    Python refuses -- ffmpeg reads anything and hands over plain 16 bit.
    """
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", "%.3f" % from_s, "-t",
         "%.3f" % (to_s - from_s), "-i", path, "-ac", "1", "-ar",
         str(RATE), "-f", "s16le", "-"], check=True,
        capture_output=True).stdout
    x = np.frombuffer(out, "<i2").astype(float)
    spectrum = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    return np.fft.rfftfreq(len(x), 1.0 / RATE)[int(np.argmax(spectrum))]


a = loudest_hz(target, 0.1, 0.9)
b = loudest_hz(target, 1.1, 1.9)
check("the first named file is first", abs(a - 440.0) < 20.0, "%.0f Hz" % a)
check("the second one second", abs(b - 1500.0) < 20.0, "%.0f Hz" % b)

print("\n4. An unused input is never one side of a stereo track")
# The interface offers no tick where the neighbour is silent, but a tick
# made earlier outlives the measurement: take a block away and a channel
# that carried something may not any more.
f = {"channels": 3, "silent": [False, False, True], "readable": True,
     "level": [-20.0, -20.0, -120.0],
     "pair_same": [0.0, None], "pair_zero": [0.1, None],
     "pair_apart": [0.0, None]}
check("the stored tick is not honoured against a silent channel",
      vpm.joined_channels(f, {1: True}) == {}, str(vpm.joined_channels(f, {1: True})))
tracks = vpm.channel_tracks(f, "X", {1: True})
check("so channel 2 stays a track of its own",
      [t[0] for t in tracks] == [(0,), (1,), (2,)], str([t[0] for t in tracks]))
live = {"channels": 3, "silent": [False, False, False], "readable": True,
        "level": [-20.0, -20.0, -20.0],
        "pair_same": [0.0, 0.0], "pair_zero": [0.1, 0.1],
        "pair_apart": [0.0, 0.0]}
check("where both carry something the tick still counts",
      vpm.joined_channels(live, {1: True}) == {1: True})

print("\n5. A file named by hand that cannot be used is said out loud")
solo = tone("r_260809_000030.wav", 300.0)
other = tone("x_260809_010000.wav", 300.0)
rows = vpm.group_recording_parts(
    [solo, other], together=[[solo, os.path.join(WORK, "nope.wav")]])
said = " ".join(why for _row, discarded in rows
                for _name, why in discarded) + " " + " ".join(
    name for _row, discarded in rows for name, _why in discarded)
check("the missing file is named", "nope.wav" in said, said[:160])

print("\n6. Two file names for the same moment say why nothing was joined")
# Five minutes apart, so the trailing number cannot stand in for the
# clock: 140000 and 140500 are not two consecutive counts, and only the
# clock rule can join them.


def long_silence(name, seconds):
    """A file of this length without the bytes -- only the length is read."""
    path = os.path.join(WORK, name)
    n = int(seconds * vpm.SR)
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + n * 2) + b"WAVE"
                + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, vpm.SR,
                                        vpm.SR * 2, 2, 16)
                + b"data" + struct.pack("<I", n * 2))
        f.seek(n * 2 - 1, 1)
        f.write(b"\x00")
    return path


long_silence("v_260808_140000.wav", 300.0)
long_silence("v_20260808_140000.wav", 300.0)
after = long_silence("v_260808_140500.wav", 300.0)
row, discarded = vpm.find_continuation_files(after)
check("neither of the two is taken", len(row) == 1, str(len(row)))
check("and the reason is given", bool(discarded), str(discarded))
check("naming both files",
      len([1 for name, _why in discarded if name.startswith("v_")]) >= 2,
      str(discarded))

print("\n7. A mono mixdown is not taken for a stereo one")
# On resume the existing outputs are read back. The answer names the file
# but not always its channel count; where it does, that count decides,
# or a stereo run would keep the one-channel yardstick from before.
mono_there = [{"format": "wav", "filename": "Show_master.wav",
               "mono_mixdown": True}]
want_stereo = [{"format": "wav", "suffix": "_master", "mono_mixdown": False}]
check("the two-channel one is still missing",
      vpm.missing_outputs(mono_there, want_stereo) == want_stereo,
      str(vpm.missing_outputs(mono_there, want_stereo)))
check("and the one that is there is not asked for again",
      vpm.missing_outputs(mono_there, [dict(want_stereo[0],
                                            mono_mixdown=True)]) == [])
unsaid = [{"format": "wav", "filename": "Show_master.wav"}]
check("where the answer says nothing, nothing is sent twice",
      vpm.missing_outputs(unsaid, want_stereo) == [],
      str(vpm.missing_outputs(unsaid, want_stereo)))
# An empty channel count is not a channel count of one. Read as "mono:
# no", it made every resume of a mono production send the master a
# second time -- and auphonic.com appends rather than replaces, so it
# would be computed and billed twice.
empty = [{"format": "wav", "filename": "Show_master.wav",
          "mono_mixdown": None}]
check("an empty channel count counts as no answer",
      vpm.missing_outputs(empty, want_stereo) == [],
      str(vpm.missing_outputs(empty, want_stereo)))
# An output that is configured but never rendered has no file name to
# read a suffix from. It carries its own.
planned = [{"format": "wav", "suffix": "_master", "mono_mixdown": False}]
check("a configured output is found by its own suffix",
      vpm.missing_outputs(planned, want_stereo) == [],
      str(vpm.missing_outputs(planned, want_stereo)))
check("and one that says nothing about its channels counts for both",
      vpm.missing_outputs([{"format": "wav", "suffix": "_master"}],
                          want_stereo) == [])
check("and a stated one channel still asks for the two channel one",
      vpm.missing_outputs(
          [{"format": "wav", "filename": "Show_master.wav",
            "mono_mixdown": True}],
          [dict(want_stereo[0], mono_mixdown=False)]) != [])

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("all checks passed")
