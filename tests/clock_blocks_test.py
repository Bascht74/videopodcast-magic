# -*- coding: utf-8 -*-
"""Blocks that carry a clock in the name instead of a counter.

A recorder numbers its files and the next block is the next number. A
mixer often writes the date and the time of day instead, which are not
consecutive numbers. The rule here: the clock of the next block has to
sit where the previous one ends.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, struct, sys, tempfile
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="clockblocks_")
bad = []


def check(what, ok, detail=""):
    print("%-58s %s%s" % (what, "ok" if ok else "FAIL",
                          "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


def wav(name, seconds):
    """A silent file of exactly this length -- only the length is read."""
    path = os.path.join(WORK, name)
    n = int(seconds * vpm.SR)
    head = (b"RIFF" + struct.pack("<I", 36 + n * 2) + b"WAVE"
            + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, vpm.SR,
                                    vpm.SR * 2, 2, 16)
            + b"data" + struct.pack("<I", n * 2))
    with open(path, "wb") as f:
        f.write(head)
        f.write(b"\x00" * (n * 2))
    return path


def names(row):
    return [os.path.basename(x) for x in row]


#------------------------------------------------------------ reading a clock
check("a date and a time are read",
      vpm.clock_in_name("r_260808_185628") is not None)
check("and the rest of the name comes with it",
      vpm.clock_in_name("r_260808_185628")[1:] == ("r_", ""))
check("a four digit year works as well",
      vpm.clock_in_name("mix_20260808_185628") is not None)
check("a counter is not a clock",
      vpm.clock_in_name("Moderator_REC00009") is None)
check("nor is a camera name",
      vpm.clock_in_name("Kandidat_08141858_C009") is None)
check("six digits that are no date are refused",
      vpm.clock_in_name("Take_991399_120000") is None)
one = vpm.clock_in_name("r_260808_185628")[0]
two = vpm.clock_in_name("r_260808_190128")[0]
check("and the difference is the five minutes it looks like",
      abs((two - one) - 300.0) < 0.001, "%.1f s" % (two - one))

#-------------------------------------------------------- the blocks join up
a = wav("r_260808_185628.wav", 300.0)
b = wav("r_260808_190128.wav", 300.0)
c = wav("r_260808_190628.wav", 300.0)
later = wav("r_260808_191500.wav", 120.0)

row, discarded = vpm.find_continuation_files(a)
check("three blocks in a row are found", names(row) == [
    "r_260808_185628.wav", "r_260808_190128.wav", "r_260808_190628.wav"],
    str(names(row)))
check("the later take stays out",
      "r_260808_191500.wav" in [n for n, _why in discarded],
      str(discarded))
row2, _ = vpm.find_continuation_files(b)
check("picking a middle block finds the same row", names(row2) == names(row))
row3, _ = vpm.find_continuation_files(c)
check("picking the last one too", names(row3) == names(row))
row4, _ = vpm.find_continuation_files(later)
check("the later take is a recording of its own",
      names(row4) == ["r_260808_191500.wav"], str(names(row4)))

got = vpm.group_recording_parts([a, b, c, later])
check("so the four files are two recordings", len(got) == 2, str(len(got)))
check("three blocks in the first", len(got[0][0]) == 3)

#---------------------------------------------------------- a gap breaks it
gap = wav("s_260808_120000.wav", 300.0)
after_gap = wav("s_260808_121000.wav", 300.0)     # five minutes too late
row5, discarded5 = vpm.find_continuation_files(gap)
check("a block that starts too late is not appended",
      names(row5) == ["s_260808_120000.wav"], str(names(row5)))
check("and the reason is given", bool(discarded5), str(discarded5))

#--------------------------------- two names spelling the same moment
# "260808" and "20260808" are the same day, and which file is meant
# cannot be decided -- so neither is taken.
same_a = wav("v_260808_140000.wav", 300.0)
same_b = wav("v_20260808_140000.wav", 300.0)
after_both = wav("v_260808_140500.wav", 300.0)
rowx, _dx = vpm.find_continuation_files(after_both)
check("a moment claimed twice joins nothing",
      names(rowx) == ["v_260808_140500.wav"], str(names(rowx)))
got = vpm.group_recording_parts([same_a, same_b, after_both])
flat = [x for r, _d in got for x in r]
check("and no file lands in two recordings",
      len(flat) == len(set(flat)), str([os.path.basename(x) for x in flat]))

#--------------------------------------- a clock that is only the session
d1 = wav("t_260808_090000_01.wav", 60.0)
d2 = wav("t_260808_090000_02.wav", 60.0)
row6, _ = vpm.find_continuation_files(d1)
check("where every block carries the same clock the counter still works",
      names(row6) == ["t_260808_090000_01.wav", "t_260808_090000_02.wav"],
      str(names(row6)))

#------------------------------- a counter that reads as a time of day
# "000001" is a valid time, so the clock rule fires and finds nothing.
# The counter rule has to get its turn afterwards.
f1 = wav("w_260808_000001.wav", 300.0)
f2 = wav("w_260808_000002.wav", 300.0)
f3 = wav("w_260808_000003.wav", 300.0)
row7, _d7 = vpm.find_continuation_files(f1)
check("the counter still finds them", names(row7) == [
    "w_260808_000001.wav", "w_260808_000002.wav", "w_260808_000003.wav"],
    str(names(row7)))

#--------------------------------------------------- different name, no row
e1 = wav("u_260808_140000.wav", 300.0)
e2 = wav("other_260808_140500.wav", 300.0)
row7, _ = vpm.find_continuation_files(e1)
check("a different name is a different recording",
      names(row7) == ["u_260808_140000.wav"], str(names(row7)))

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("all checks passed")
