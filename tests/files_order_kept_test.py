# -*- coding: utf-8 -*-
"""Files put together by hand keep the order they were named in.

Sorting by name is right for what the search found on its own. A row
named by hand carries an order somebody chose, and sorting that row
throws the choice away. In order: the material stands on disc, the row
comes back whole, it keeps the order it was named in, and it travels as
one block ranked under the alphabetically smallest name in it -- a
loose file sorts ahead of the whole row or behind it, never into it.
Without --together the same files sort by name.

The files are empty: only their order is measured.
"""
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
import importlib.util
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


def names(files):
    """The bare file names, in the order they came back."""
    return [os.path.basename(x) for x in files]


folder = tempfile.mkdtemp(prefix="vpm_together_")
# The row, in the order somebody typed it: not alphabetical, and its
# smallest name is neither the first nor the last of the three.
row = [os.path.join(folder, x)
       for x in ("Zulu.wav", "Alpha.wav", "Mike.wav")]
# Two loose files, one on each side of the row's smallest name
# ("Alpha.wav"), so both directions of the ranking get asked.
behind = os.path.join(folder, "Bravo.wav")
ahead = os.path.join(folder, "Aaron.wav")
for p in row + [behind, ahead]:
    open(p, "wb").close()

# The material first: every claim below is about the order of a list of
# files, and a file that never reached the disc would be reported as an
# order that came out wrong.
there = [p for p in row + [behind, ahead] if os.path.isfile(p)]
check("the material stands on disc before anything is collected",
      len(there) == 5,
      "5 wanted, %d created: %s" % (len(there), names(there)))

out, _ = vpm.collect_with_continuations(row, True, together=[row])
check("a hand-forced row comes back with every file it names",
      sorted(names(out)) == ["Alpha.wav", "Mike.wav", "Zulu.wav"],
      "3 wanted ['Alpha.wav', 'Mike.wav', 'Zulu.wav'], %d back %s"
      % (len(out), sorted(names(out))))
check("a hand-forced row keeps the order it was named in",
      names(out) == ["Zulu.wav", "Alpha.wav", "Mike.wav"],
      "wanted ['Zulu.wav', 'Alpha.wav', 'Mike.wav'], got %s" % (names(out),))

out, _ = vpm.collect_with_continuations(
    row + [behind], True, together=[row])
check("a loose file beside a hand-forced row is not lost",
      sorted(names(out))
      == ["Alpha.wav", "Bravo.wav", "Mike.wav", "Zulu.wav"],
      "4 wanted ['Alpha.wav', 'Bravo.wav', 'Mike.wav', 'Zulu.wav'], "
      "%d back %s" % (len(out), sorted(names(out))))
check("a loose name after the row's smallest sorts behind the row",
      names(out) == ["Zulu.wav", "Alpha.wav", "Mike.wav", "Bravo.wav"],
      "wanted ['Zulu.wav', 'Alpha.wav', 'Mike.wav', 'Bravo.wav'], got %s"
      % (names(out),))

out, _ = vpm.collect_with_continuations(
    row + [ahead], True, together=[row])
check("a loose name before the row's smallest sorts ahead of the row",
      names(out) == ["Aaron.wav", "Zulu.wav", "Alpha.wav", "Mike.wav"],
      "wanted ['Aaron.wav', 'Zulu.wav', 'Alpha.wav', 'Mike.wav'], got %s"
      % (names(out),))

out, _ = vpm.collect_with_continuations(row + [behind], True)
check("without --together everything sorts by name",
      names(out) == ["Alpha.wav", "Bravo.wav", "Mike.wav", "Zulu.wav"],
      "wanted ['Alpha.wav', 'Bravo.wav', 'Mike.wav', 'Zulu.wav'], got %s"
      % (names(out),))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
