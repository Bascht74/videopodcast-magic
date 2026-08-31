# -*- coding: utf-8 -*-
"""The channels are judged over the whole recording, not over one block.

A soundcheck block can read as one used channel pair where the show
reads as ten tracks, so judging one block alone throws tracks away.
Each block is measured on its own -- they do not all fit in memory --
and a channel counts as used where it carries anything in any block,
the pair judgement coming from the block where the pair is loudest.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, struct, sys, tempfile, time
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
SR = vpm.SR
WORK = tempfile.mkdtemp(prefix="blocksfacts_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def voice(seed, n):
    """Speech-like noise in bursts, so the pair judgement has something."""
    r = np.random.default_rng(seed)
    x = np.zeros(n)
    t = 0
    while t < n - SR:
        length = int(r.uniform(0.15, 0.45) * SR)
        block = r.normal(size=length)
        spectrum = np.fft.rfft(block)
        f = np.fft.rfftfreq(length, 1.0 / SR)
        spectrum[(f < 200) | (f > 3000)] = 0
        piece = np.fft.irfft(spectrum, length)
        piece /= (np.abs(piece).max() or 1.0)
        x[t:t + length] += 0.5 * np.hanning(length) * piece
        t += length + int(r.uniform(0.1, 0.4) * SR)
    return x


def write(path, columns):
    x = np.stack(columns, axis=1)
    ch = x.shape[1]
    b = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + len(b)) + b"WAVE")
        f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, ch, SR,
                                      SR * 2 * ch, 2 * ch, 16))
        f.write(b"data" + struct.pack("<I", len(b)) + b)
    return path


DURATION = 12.0
n = int(DURATION * SR)
a = voice(11, n)
b = voice(22, n)
hush = np.zeros(n)

# Block one: only channels 1 and 2 carry anything, and under the floor.
one = write(os.path.join(WORK, "Mix_01.wav"),
            [a * 0.00002, b * 0.00002, hush, hush])
# Block two: the same channels with the recording on them. One and two
# are microphones far apart, three and four a pair.
def late(x, ms):
    d = int(round(ms / 1000.0 * SR))
    y = np.zeros_like(x)
    y[d:] = x[:len(x) - d]
    return y


# Three and four stand together elsewhere in the room, so both hear
# both voices, and equally late. That delay is what tells them apart
# from their neighbour: three shares plenty with two, but not in time.
two = write(os.path.join(WORK, "Mix_02.wav"),
            [a + 0.05 * late(b, 6.0),
             b + 0.05 * late(a, 6.0),
             0.6 * late(a, 3.0) + 0.6 * late(b, 3.0),
             0.5 * late(a, 3.0) + 0.7 * late(b, 3.0)])

first = vpm.channel_facts_cached(one)
second = vpm.channel_facts_cached(two)
both = vpm.blocks_facts([one, two])

check("the quiet block on its own has nothing left",
      all(first["silent"]), str(first["silent"]))
check("the loud block has all four channels",
      not any(second["silent"]), str(second["silent"]))
check("together, the recording has all four", not any(both["silent"]),
      str(both["silent"]))
check("and the levels are the louder block's",
      both["level"] == second["level"],
      "%s against %s" % (both["level"], second["level"]))

pairs = vpm.channel_joins(both)
check("three neighbours are judged", len(pairs) == 3, str(len(pairs)))
check("channels 1 and 2 are read as two microphones",
      pairs[0][1] is False, str(pairs[0]))
check("channels 3 and 4 as one stereo track",
      pairs[2][1] is True, str(pairs[2]))
check("the judgement is the loud block's",
      [p[1] for p in pairs] == [q[1] for q in vpm.channel_joins(second)])

tracks = vpm.channel_tracks(both, "Mix")
check("so the recording gives three tracks",
      len([t for t in tracks if not t[2]]) == 3,
      str([t[1] for t in tracks if not t[2]]))

#---------------------------------- the pair is judged where it was audible
# A block where one of the two channels is silent measures nothing for
# that pair, so the loudest block overall may hold no answer at all.
def facts(level, zero):
    n = len(level)
    highest = max(level)
    silent = [x < highest - vpm.SILENT_BELOW_DB or x < vpm.QUIET_BELOW_DBFS
              for x in level]
    return {"channels": n, "level": level, "silent": silent,
            "pair_same": [None] * (n - 1), "pair_zero": list(zero),
            "pair_apart": [None] * (n - 1), "readable": True}


loud_but_blind = facts([-20.0, -20.0, -30.0, -110.0], [0.9, 0.1, None])
quiet_but_seeing = facts([-40.0, -40.0, -45.0, -45.0], [0.9, 0.1, 0.95])
kept = dict(vpm._PROBE)
try:
    vpm.channel_facts_cached = lambda p: (loud_but_blind if p == "loud"
                                          else quiet_but_seeing)
    both = vpm.blocks_facts(["loud", "quiet"])
    pairs = vpm.channel_joins(both)
    check("the pair is judged in the block that could see it",
          len(pairs) == 3 and pairs[2][1] is True,
          str(pairs[2] if len(pairs) > 2 else pairs))
    check("and it is not reported as unmeasurable",
          "not recognisable" not in (pairs[2][3] if len(pairs) > 2 else ""),
          str(pairs[2][3] if len(pairs) > 2 else ""))
finally:
    vpm.channel_facts_cached = lambda p: vpm.probe_remember(
        "channelfacts", p, lambda: vpm.channel_facts(p))
    vpm._PROBE.clear()
    vpm._PROBE.update(kept)

#------------------------------------------------------- the simple cases
check("one block alone is just that block's answer",
      vpm.blocks_facts([two])["silent"] == second["silent"])
check("no blocks at all is not readable",
      vpm.blocks_facts([])["readable"] is False)

#--------------------------------------------------- what has to match to join
mono = write(os.path.join(WORK, "Mono_01.wav"), [a])
fits, why = vpm.shapes_match(one, two)
check("two blocks of the same shape fit", fits and not why)
fits, why = vpm.shapes_match(one, mono)
check("a different channel count does not", not fits, why)
check("and the reason names both counts", "4" in why and "1" in why, why)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
