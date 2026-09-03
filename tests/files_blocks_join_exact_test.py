# -*- coding: utf-8 -*-
"""Blocks join only where the file names match letter for letter.

A recorder numbers its files and the next block is the next number.
The number is looked for in the name exactly as the first block writes
it: a name that differs in its spelling is a different recording, not
the same one written twice. Both directions are asked, because a rule
that joins nothing passes every judgement of the first kind.

The limit of the method: the two spellings cannot lie side by side on
a case-insensitive disc, so only one of them is ever written here, and
what is measured is that the search does not reach for the other.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, struct, sys, tempfile, time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="exactblocks_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def wav(folder, name, seconds):
    """A silent file of exactly this length -- only the length is read."""
    path = os.path.join(folder, name)
    n = int(seconds * vpm.SR)
    head = (b"RIFF" + struct.pack("<I", 36 + n * 2) + b"WAVE"
            + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, vpm.SR,
                                    vpm.SR * 2, 2, 16)
            + b"data" + struct.pack("<I", n * 2))
    with open(path, "wb") as f:
        f.write(head)
        f.write(b"\x00" * (n * 2))
    return path


def card(which):
    """A folder of its own, so one reading cannot see the other's files."""
    path = os.path.join(WORK, which)
    os.makedirs(path)
    return path


def names(row):
    return sorted(os.path.basename(x) for x in row)


print("1. The same spelling: the blocks are one recording")
# Without this the judgement below would pass on a rule that refuses
# everything, and nothing here would say so.
same = card("same")
first = wav(same, "REC0001.wav", 60.0)
wav(same, "REC0002.wav", 60.0)
row, _thrown = vpm.find_continuation_files(first)
check("two blocks written alike arrive as one recording",
      names(row) == ["REC0001.wav", "REC0002.wav"],
      "%s, wanted both blocks" % (names(row),))

print("\n2. A different spelling is a different recording")
# The second block is written in lower case. On a case-sensitive disc
# these are two files, so folding them together would answer one way
# there and another way here.
apart = card("apart")
lone = wav(apart, "REC0001.wav", 60.0)
wav(apart, "rec0002.wav", 60.0)
row2, _t2 = vpm.find_continuation_files(lone)
check("a block spelt differently is not joined",
      names(row2) == ["REC0001.wav"],
      "%s, wanted ['REC0001.wav'] out of %s"
      % (names(row2), sorted(os.listdir(apart))))
# And the same the other way about, so the answer does not depend on
# which of the two the reading starts from.
row3, _t3 = vpm.find_continuation_files(os.path.join(apart,
                                                     "rec0002.wav"))
check("and not from the other end either",
      names(row3) == ["rec0002.wav"],
      "%s, wanted ['rec0002.wav'] out of %s"
      % (names(row3), sorted(os.listdir(apart))))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
