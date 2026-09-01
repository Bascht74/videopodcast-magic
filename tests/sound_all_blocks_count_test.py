# -*- coding: utf-8 -*-
"""The channels are judged over the whole recording, not over one block.

A soundcheck block can read as one used channel pair where the show
reads as ten tracks, so judging one block alone throws tracks away.
Each block is measured on its own -- they do not all fit in memory --
and a channel counts as used where it carries anything in any block.
Every neighbour is judged, and from the block where that pair is
loudest and could see it at all; the tracks follow from that. One block
alone is that block's answer, no block at all is unreadable, and two
blocks of unequal channel count do not fit -- the reason names both.
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


def db(level):
    """Levels rounded, so a failure line carries numbers one can read."""
    return "[" + ", ".join("%.1f" % x for x in (level or [])) + "]"


def pair(pairs, i):
    """Neighbour i, or a blank one.

    A list shorter than expected is then a FAIL with numbers in it,
    and not a traceback that takes the count of judgements with it.
    """
    return pairs[i] if i < len(pairs) else (None, None, None, "")


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
      all(first["silent"]) and len(first["silent"]) == 4,
      "%d of 4 channels left, levels %s"
      % (sum(1 for x in first["silent"] if not x), db(first["level"])))
check("the loud block has all four channels",
      not any(second["silent"]) and len(second["silent"]) == 4,
      "%d of 4 channels left, levels %s"
      % (sum(1 for x in second["silent"] if not x), db(second["level"])))
check("together, the recording has all four",
      not any(both["silent"]) and len(both["silent"]) == 4,
      "%d of 4 channels left, levels %s"
      % (sum(1 for x in both["silent"] if not x), db(both["level"])))
check("and the levels are the louder block's",
      both["level"] == second["level"],
      "%s against the loud block's %s"
      % (db(both["level"]), db(second["level"])))

pairs = vpm.channel_joins(both)
check("three neighbours are judged", len(pairs) == 3,
      "%d pairs over %d channels" % (len(pairs), both["channels"]))
check("channels 1 and 2 are read as two microphones",
      pair(pairs, 0)[1] is False,
      "stereo=%s for pair %s -- %s"
      % (pair(pairs, 0)[1], pair(pairs, 0)[0], pair(pairs, 0)[3]))
check("channels 3 and 4 as one stereo track",
      pair(pairs, 2)[1] is True,
      "stereo=%s for pair %s -- %s"
      % (pair(pairs, 2)[1], pair(pairs, 2)[0], pair(pairs, 2)[3]))
alone = [p[1] for p in vpm.channel_joins(second)]
check("the judgement is the loud block's",
      [p[1] for p in pairs] == alone,
      "%s over both blocks against %s over the loud one alone"
      % ([p[1] for p in pairs], alone))

tracks = vpm.channel_tracks(both, "Mix")
awake = [t[1] for t in tracks if not t[2]]
check("so the recording gives three tracks", len(awake) == 3,
      "%d of %d tracks carry sound: %s" % (len(awake), len(tracks), awake))

#---------------------------------- the pair is judged where it was audible
# The loudest block may hold no answer for a pair at all -- too few
# places where both channels carry sound, and nothing was measured.
# Here the loud block is the louder one on both channels of the last
# pair and still has nothing to say about it, so only a block that was
# skipped for having no answer can leave the quiet one in charge.
def facts(level, zero, silent):
    n = len(level)
    return {"channels": n, "level": list(level), "silent": list(silent),
            "pair_same": [None] * (n - 1), "pair_zero": list(zero),
            "pair_apart": [None] * (n - 1), "readable": True}


loud_but_blind = facts([-20.0, -20.0, -30.0, -32.0], [0.9, 0.1, None],
                       [False, False, False, False])
quiet_but_seeing = facts([-40.0, -40.0, -45.0, -45.0], [0.9, 0.1, 0.95],
                         [False, False, False, False])
seen = []
kept = dict(vpm._PROBE)
real_cached = vpm.channel_facts_cached
try:
    def made_up(path):
        seen.append(path)
        return loud_but_blind if path == "loud" else quiet_but_seeing

    vpm.channel_facts_cached = made_up
    made = vpm.blocks_facts(["loud", "quiet"])
    made_pairs = vpm.channel_joins(made)
finally:
    vpm.channel_facts_cached = real_cached
    vpm._PROBE.clear()
    vpm._PROBE.update(kept)

check("each block is measured on its own", seen == ["loud", "quiet"],
      "%d of 2 blocks read: %s" % (len(seen), seen))
check("the made-up blocks are judged as three neighbours too",
      len(made_pairs) == 3,
      "%d pairs over %d channels" % (len(made_pairs), made["channels"]))
check("the pair is judged in the block that could see it",
      pair(made_pairs, 2)[1] is True,
      "stereo=%s for pair %s -- %s"
      % (pair(made_pairs, 2)[1], pair(made_pairs, 2)[0],
         pair(made_pairs, 2)[3]))
# certain=False is what the two "not recognisable" answers carry, and
# nothing else does -- asked that way round the check does not have to
# quote a sentence in one language.
check("and it is not reported as unmeasurable",
      pair(made_pairs, 2)[2] is True,
      "certain=%s -- %s"
      % (pair(made_pairs, 2)[2], pair(made_pairs, 2)[3]))

#------------------------------------------------------- the simple cases
check("one block alone is just that block's answer",
      vpm.blocks_facts([two])["silent"] == second["silent"],
      "%s against the block's own %s"
      % (vpm.blocks_facts([two])["silent"], second["silent"]))
empty = vpm.blocks_facts([])
check("no blocks at all is not readable", empty["readable"] is False,
      "readable=%s over %d channels" % (empty["readable"], empty["channels"]))

#--------------------------------------------------- what has to match to join
mono = write(os.path.join(WORK, "Mono_01.wav"), [a])
fits, why = vpm.shapes_match(one, two)
check("two blocks of the same shape fit", fits and not why,
      "fits=%s, 4 channels against 4, reason %r" % (fits, why))
fits, why = vpm.shapes_match(one, mono)
check("a different channel count does not", not fits,
      "fits=%s for 4 channels against 1, reason %r" % (fits, why))
check("and the reason names both counts", "4" in why and "1" in why,
      "wanted 4 and 1 in %r" % (why,))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
