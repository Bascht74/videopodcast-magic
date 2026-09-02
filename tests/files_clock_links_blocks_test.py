# -*- coding: utf-8 -*-
"""Blocks that carry a clock in the name instead of a counter.

A recorder numbers its files and the next block is the next number. A
mixer often writes the date and the time of day instead, which are not
consecutive numbers. Two rules then: the clock of the next block has to
sit where the previous one ends, and only names built alike are joined
-- the text before the clock and the text behind it have to match, the
extension only apart from its case.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, struct, sys, tempfile, time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="clockblocks_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


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


def before_half(stem):
    """The text before the clock, or None where no clock is read."""
    read = vpm.clock_in_name(stem)
    return read[1] if read else None


#------------------------------------------------------------ reading a clock
dated = vpm.clock_in_name("r_260808_185628")
check("a date and a time are read", dated is not None,
      "r_260808_185628 reads as %s" % (dated,))
check("and the rest of the name comes with it",
      dated is not None and dated[1:] == ("r_", ""),
      "%s, wanted ('r_', '')" % (dated[1:] if dated else None,))
four_digits = vpm.clock_in_name("mix_20260808_185628")
check("a four digit year works as well", four_digits is not None,
      "mix_20260808_185628 reads as %s" % (four_digits,))
counter = vpm.clock_in_name("Presenter_REC00021")
check("a counter is not a clock", counter is None,
      "Presenter_REC00021 reads as %s, wanted nothing" % (counter,))
camera = vpm.clock_in_name("GuestCam_01011858_C003")
check("nor is a camera name", camera is None,
      "GuestCam_01011858_C003 reads as %s, wanted nothing" % (camera,))
no_date = vpm.clock_in_name("Take_991399_120000")
check("six digits that are no date are refused", no_date is None,
      "Take_991399_120000 reads as %s, wanted nothing" % (no_date,))
# Both read, or the difference cannot be taken at all -- and a test that
# dies here reports one judgement and hides the twenty-two under it.
one = vpm.clock_in_name("r_260808_185628")
two = vpm.clock_in_name("r_260808_190128")
check("and the difference is the five minutes it looks like",
      one is not None and two is not None
      and abs((two[0] - one[0]) - 300.0) < 0.001,
      "%.1f s" % (two[0] - one[0]) if one and two else
      "no clock read: %s and %s" % (one, two))

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
check("picking a middle block finds the same row", names(row2) == names(row),
      "%s, wanted %s" % (names(row2), names(row)))
row3, _ = vpm.find_continuation_files(c)
check("picking the last one too", names(row3) == names(row),
      "%s, wanted %s" % (names(row3), names(row)))
row4, _ = vpm.find_continuation_files(later)
check("the later take is a recording of its own",
      names(row4) == ["r_260808_191500.wav"], str(names(row4)))

got = vpm.group_recording_parts([a, b, c, later])
check("so the four files are two recordings", len(got) == 2, str(len(got)))
check("three blocks in the first", len(got[0][0]) == 3,
      "%d blocks, wanted 3: %s" % (len(got[0][0]), names(got[0][0])))

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

#------------------------------------------- the name has to match exactly
# Each pair sits on two moments no other file above claims, both blocks
# a minute long and a minute apart and of the same shape -- so the name
# is the only thing left that can keep them apart, which is what these
# are about. On a moment claimed twice a pair would fall out of the
# family for that reason instead, and then the whole name rule could be
# deleted with every judgement here still green (measured, 2.9.2026).
# The differences are the ones a forgiving comparison waves through: a
# longer name, another separator, another text behind the clock.
# The separator between the text and the clock belongs to the text, not
# to the clock, so widening the left edge of NAME_CLOCK moves it out of
# the name -- and then Take_ and Take- really are the same name and the
# separator judgement falls although the comparison of names is whole.
# That is why its line prints both halves: two equal halves there say
# the clock has grown, not that the name rule is broken.
p1 = wav("Presenter_260808_160000.wav", 60.0)
p2 = wav("Presenter_B_260808_160100.wav", 60.0)
row8, _ = vpm.find_continuation_files(p1)
check("a name that another only extends is a different recording",
      names(row8) == ["Presenter_260808_160000.wav"],
      "%s, wanted ['Presenter_260808_160000.wav']" % (names(row8),))

s1 = wav("Take_260808_200000.wav", 60.0)
s2 = wav("Take-260808_200100.wav", 60.0)
row10, _ = vpm.find_continuation_files(s1)
check("a name that differs only in the separator is a different recording",
      names(row10) == ["Take_260808_200000.wav"],
      "%s, wanted ['Take_260808_200000.wav']; the text before the clock "
      "reads %r against %r"
      % (names(row10), before_half("Take_260808_200000"),
         before_half("Take-260808_200100")))

g1 = wav("rec_260808_170000_Guest.wav", 60.0)
g2 = wav("rec_260808_170100_Presenter.wav", 60.0)
row11, _ = vpm.find_continuation_files(g1)
check("and the text behind the clock has to match as well",
      names(row11) == ["rec_260808_170000_Guest.wav"],
      "%s, wanted ['rec_260808_170000_Guest.wav']" % (names(row11),))

#------------------------------- the extension only apart from its case
# The one difference that has to be waved through, and the only point
# about case where both rules in the program say the same: the clock
# rule folds the extension to lower case before comparing, and the
# counter rule beside it takes a name that differs only in case as long
# as it is the only one that could be meant. Whether the text before
# and behind the clock is read as forgivingly the two rules answer
# differently, and nothing here decides that.
e1 = wav("Mix_260808_183000.wav", 60.0)
e2 = wav("Mix_260808_183100.WAV", 60.0)
row12, _ = vpm.find_continuation_files(e1)
check("a block whose extension differs only in case still joins",
      names(row12) == ["Mix_260808_183000.wav", "Mix_260808_183100.WAV"],
      "%s, wanted ['Mix_260808_183000.wav', 'Mix_260808_183100.WAV']"
      % (names(row12),))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
