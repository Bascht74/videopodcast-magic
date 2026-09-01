# -*- coding: utf-8 -*-
"""Putting files into one recording by hand.

The counterpart to --apart, for names that give the search nothing to go
on: no counter, no clock. Each name brings the blocks already found for
it, so naming one block of a chain brings the whole chain.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, struct, sys, tempfile, time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="together_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def wav(name, seconds=1.0):
    path = os.path.join(WORK, name)
    n = int(seconds * vpm.SR)
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + n * 2) + b"WAVE")
        f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, vpm.SR,
                                      vpm.SR * 2, 2, 16))
        f.write(b"data" + struct.pack("<I", n * 2) + b"\x00" * (n * 2))
    return path


def names(rows):
    return [[os.path.basename(x) for x in r] for r, _d in rows]


#--------------------------------------------------------- merging the groups
check("two groups sharing a file become one",
      vpm.together_chains([["a", "b"], ["b", "c"]])
      == [[os.path.abspath(x) for x in ("a", "b", "c")]],
      str(vpm.together_chains([["a", "b"], ["b", "c"]])))
alone = vpm.together_chains([["a"]])
check("a group of one says nothing", alone == [],
      "%d chains %s, wanted none" % (len(alone), alone))
empty = vpm.together_chains([])
check("nothing given, nothing back", empty == [],
      "%d chains %s, wanted none" % (len(empty), empty))
named = [os.path.basename(x) for x in vpm.together_chains([["z", "a"]])[0]]
check("order is the order they were named in", named == ["z", "a"],
      "%s, wanted ['z', 'a']" % (named,))

#--------------------------------------------------------- the grouping itself
one = wav("Alpha.wav")
two = wav("Bravo.wav")
three = wav("Charlie.wav")
every = [one, two, three]

separate = vpm.group_recording_parts(every)
check("nothing joined: three recordings", len(separate) == 3,
      "%d recordings %s, wanted 3" % (len(separate), names(separate)))
got = vpm.group_recording_parts(every, together=[[one, three]])
check("two put together: two recordings", len(got) == 2, str(names(got)))
check("and they are in the order they were named",
      names(got)[0] == ["Alpha.wav", "Charlie.wav"]
      or names(got)[1] == ["Alpha.wav", "Charlie.wav"], str(names(got)))
check("the third stands alone",
      ["Bravo.wav"] in names(got), str(names(got)))

#------------------------------------------------- a named file brings its own
a1 = wav("Rec_01.wav")
a2 = wav("Rec_02.wav")
loose = wav("Extra.wav")
row = vpm.group_recording_parts([a1, a2, loose])
check("the two numbered blocks are found on their own",
      len(row) == 2, str(names(row)))
row = vpm.group_recording_parts([a1, a2, loose], together=[[a1, loose]])
check("joining the first block brings the second along",
      len(row) == 1 and names(row)[0] == ["Rec_01.wav", "Rec_02.wav",
                                          "Extra.wav"],
      str(names(row)))

#-------------------------------------------------------------- apart wins
row = vpm.group_recording_parts([a1, a2, loose], apart=[a2],
                                together=[[a1, loose]])
check("a block set apart stays out of the group",
      names(row)[0] == ["Rec_01.wav", "Extra.wav"], str(names(row)))
check("and is a recording of its own", ["Rec_02.wav"] in names(row),
      str(names(row)))

#--------------------------------------------- the same for the file collector
out, _hints = vpm.collect_with_continuations([one], False,
                                             together=[[one, three]])
check("collecting one file brings what was joined to it",
      [os.path.basename(x) for x in out] == ["Alpha.wav", "Charlie.wav"],
      str([os.path.basename(x) for x in out]))

#------------------------------------------------- a block belongs to one row
# Two groups naming two blocks of one chain both reach for the whole
# chain. The first to claim it keeps it: a block in two recordings would
# be decoded and mixed into two productions.
row = vpm.group_recording_parts([a1, a2, one, three],
                                together=[[a1, one], [a2, three]])
flat = [x for r, _d in row for x in r]
check("no block lands in two recordings", len(flat) == len(set(flat)),
      str(names(row)))
check("and none is lost", set(os.path.basename(x) for x in flat)
      == {"Rec_01.wav", "Rec_02.wav", "Alpha.wav", "Charlie.wav"},
      str(names(row)))
check("the second group is told what happened",
      any("already in another recording" in why
          for _r, d in row for _n, why in d), str(row))

#------------------------------------------------- a name that is not there
row = vpm.group_recording_parts([one, two],
                                together=[[one, "/nowhere/Gues.wav"]])
check("a file that does not exist is refused",
      any(why == "not found" for _r, d in row for _n, why in d), str(row))
check("and the rest carries on",
      sorted(names(row)) == [["Alpha.wav"], ["Bravo.wav"]], str(names(row)))

#-------------------------------------------------------------- the switch
ap = vpm.build_argument_parser()
args = ap.parse_args(["x.wav", "--together", one, three,
                      "--together", a1, loose])
check("--together is repeatable", len(args.together) == 2,
      str(args.together))
check("and takes several files at once", len(args.together[0]) == 2,
      "%d files in the first group %s, wanted 2"
      % (len(args.together[0]),
         [os.path.basename(x) for x in args.together[0]]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
