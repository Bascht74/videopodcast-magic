# -*- coding: utf-8 -*-
"""Split blocks are found again by the names they carry today.

The name a split writes says which channels are in the piece, and the
mark that tells such a piece from the next block of the same recording
is found in that name -- so the search for continuation blocks leaves
the piece alone. What was cut is then regrouped channel by channel
across the blocks, and a recording whose blocks did not all come apart
the same way stays whole instead of putting two signals on one row.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, shutil, sys, tempfile, time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
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


def stem_of(path):
    return os.path.splitext(os.path.basename(path))[0]


# Matching the piece names against an older spelling found nothing, and
# a recording of several blocks then never came apart into tracks.
FOLDER = tempfile.mkdtemp(prefix="vpm_split_found_")
BLOCK1 = "/card1/REC0001.WAV"
BLOCK2 = "/card1/REC0002.WAV"
one = vpm.split_target(BLOCK1, (0,), FOLDER)
two = vpm.split_target(BLOCK2, (0,), FOLDER)
pair1 = vpm.split_target(BLOCK1, (1, 2), FOLDER)
pair2 = vpm.split_target(BLOCK2, (1, 2), FOLDER)

# --- the name a split writes -------------------------------------------
check("a piece of one channel is named after that channel",
      os.path.basename(one).endswith("_Channel1.wav"),
      "%s, wanted an end of _Channel1.wav" % os.path.basename(one))
check("a piece of two channels is named after both of them",
      os.path.basename(pair1).endswith("_Channel2+3.wav"),
      "%s, wanted an end of _Channel2+3.wav" % os.path.basename(pair1))

# --- the mark the block search goes by ---------------------------------
hit_one = vpm.SPLIT_MARK.search(stem_of(one))
hit_pair = vpm.SPLIT_MARK.search(stem_of(pair1))
check("the mark is found in the name of a one-channel piece",
      hit_one is not None,
      "%s in %s, wanted a mark"
      % (hit_one.group(0) if hit_one else "nothing", stem_of(one)))
check("the mark is found in the name of a two-channel piece",
      hit_pair is not None,
      "%s in %s, wanted a mark"
      % (hit_pair.group(0) if hit_pair else "nothing", stem_of(pair1)))

# The pieces have to lie in a folder the search can read, or it never
# gets as far as looking at the neighbour it must not take.
open(one, "wb").close()
open(vpm.split_target(BLOCK1, (1,), FOLDER), "wb").close()
row, discarded = vpm.find_continuation_files(one)
check("the search for the next block leaves a split piece alone",
      row == [one] and not discarded,
      "%d files back and %d put aside, wanted 1 and 0: %s"
      % (len(row), len(discarded), [os.path.basename(x) for x in row]))

# --- what a split is regrouped into ------------------------------------
alike = {BLOCK1: [one, pair1], BLOCK2: [two, pair2]}
rows = vpm.expand_chains_to_tracks(
    [([BLOCK1, BLOCK2], [])], lambda x: alike.get(x) or [])
check("two blocks cut alike give one recording per channel",
      len(rows) == 2, "%d recordings out of 2 blocks by 2 channels, "
      "wanted 2" % len(rows))
check("each of those recordings holds both blocks",
      bool(rows) and all(len(r) == 2 for r, _d in rows),
      "%s blocks per recording, wanted [2, 2]"
      % [len(r) for r, _d in rows])
first = rows[0][0] if rows else []
check("the first recording holds channel 1 of both blocks",
      first == [one, two],
      "%s, wanted %s" % ([os.path.basename(x) for x in first],
                         [os.path.basename(one), os.path.basename(two)]))

# --- blocks that did not come apart the same way -----------------------
other_way = {BLOCK1: [one, pair1],
             BLOCK2: [vpm.split_target(BLOCK2, (0, 1), FOLDER),
                      vpm.split_target(BLOCK2, (2,), FOLDER)]}
kept = vpm.expand_chains_to_tracks(
    [([BLOCK1, BLOCK2], [])], lambda x: other_way.get(x) or [])
check("blocks cut into different channels stay whole",
      len(kept) == 1,
      "%d recordings out of 1+2 against 2+3, wanted 1" % len(kept))
fewer = {BLOCK1: [one, pair1], BLOCK2: [two]}
short = vpm.expand_chains_to_tracks(
    [([BLOCK1, BLOCK2], [])], lambda x: fewer.get(x) or [])
check("blocks cut into a different number of pieces stay whole",
      len(short) == 1,
      "%d recordings out of 2 pieces against 1, wanted 1" % len(short))

shutil.rmtree(FOLDER, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
