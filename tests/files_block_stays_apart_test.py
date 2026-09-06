# -*- coding: utf-8 -*-
"""A block taken out of a recording by hand stays out."""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import shutil, subprocess, sys, tempfile, time, wave
import numpy as np
vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))

RATE = 48000
folder = tempfile.mkdtemp(prefix="vpm_apart_")


def block(name, seconds=4.0, hz=300.0):
    path = os.path.join(folder, name)
    t = np.arange(int(seconds * RATE)) / float(RATE)
    x = 0.4 * np.sin(2 * np.pi * hz * t)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes((x * 32767).astype("<i2").tobytes())
    return path


one = block("REC0001.wav")
two = block("REC0002.wav")
three = block("REC0003.wav")
other = block("Guest0001.wav", hz=700.0)
every = [one, two, three, other]

print("1. Without a mark the blocks belong together")
chains = vpm.group_recording_parts(every)
check("two recordings out of four files", len(chains) == 2, str(len(chains)))
long_one = max(chains, key=lambda c: len(c[0]))
check("and one of them has three blocks", len(long_one[0]) == 3,
      str([os.path.basename(x) for x in long_one[0]]))

print("\n2. A marked block stands on its own")
chains = vpm.group_recording_parts(every, apart=[two])
rows = sorted([sorted(os.path.basename(x) for x in row)
               for row, _d in chains])
check("three recordings now", len(chains) == 3, str(rows))
check("the marked one is alone", ["REC0002.wav"] in rows, str(rows))
check("and the rest stays together",
      ["REC0001.wav", "REC0003.wav"] in rows, str(rows))

print("\n3. It is not fetched back in either")
# Only the first block is selected: the others are found in the folder.
chains = vpm.group_recording_parts([one], apart=[two])
check("the search skips the marked block",
      [os.path.basename(x) for x in chains[0][0]]
      == ["REC0001.wav", "REC0003.wav"],
      str([os.path.basename(x) for x in chains[0][0]]))
# The line above reads one recording. This one reads every recording the
# run would process, so a marked block landing in a neighbouring row --
# or in a row of its own -- is caught as well.
every_row = [os.path.basename(x)
             for r, _d in vpm.group_recording_parts([one, other],
                                                    apart=[two])
             for x in r]
check("and so does the run",
      sorted(every_row)
      == ["Guest0001.wav", "REC0001.wav", "REC0003.wav"],
      "%d files back: %s" % (len(every_row), sorted(every_row)))

def shown(chains):
    """The grouping as the check compares it, minus the folder name."""
    return str(chains).replace(folder + os.sep, "")


print("\n4. The whole recording knows its blocks")
family = vpm.recording_family(one)
check("all three are named", len(family) == 3, str(sorted(
    os.path.basename(x) for x in family)))
check("the other recording is not in it",
      os.path.abspath(other) not in family,
      "%d in the family: %s -- %s wanted out"
      % (len(family), sorted(os.path.basename(x) for x in family),
         os.path.basename(other)))
from_three = vpm.recording_family(three)
check("and it works from any block", from_three == family,
      "from the third block %s, from the first %s"
      % (sorted(os.path.basename(x) for x in from_three),
         sorted(os.path.basename(x) for x in family)))

print("\n5. Nothing marked, nothing changed")
with_empty = vpm.group_recording_parts(every, apart=[])
without_mark = vpm.group_recording_parts(every)
check("an empty mark is the same as none", with_empty == without_mark,
      "with an empty mark %s, with none %s"
      % (shown(with_empty), shown(without_mark)))
ghost = vpm.group_recording_parts(every, apart=["/nowhere.wav"])
check("and a mark on a file nobody has changes nothing", len(ghost) == 2,
      "%d recordings against an expected 2: %s" % (len(ghost), shown(ghost)))

print("\n6. And the plan keeps it apart")
# The five sections above ask the grouping function, and they were green
# for months while the switch did nothing: the plan rows are merged by
# speaker name one step later, and two blocks of one recorder guess the
# same name. So this one asks a whole run instead of a function.
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
           VPM_SILENT="1", VPM_NO_UPDATE_CHECK="1")


def recorder_rows(*more):
    """How many plan rows a dry run gives the recorder called REC."""
    p = subprocess.run(
        [sys.executable, SCRIPT, "--dry-run", "--without-auphonic",
         "--no-preflight", "--out", os.path.join(folder, "out")]
        + list(more) + every,
        capture_output=True, text=True, env=ENV)
    rows, keep = [], False
    for line in (p.stdout or "").splitlines():
        if "RECOGNISED PLAN" in line:
            keep = True
            continue
        if keep and line.startswith("  ") and ".wav" in line:
            rows.append(" ".join(line.split()))
        elif keep and line.strip() and not line.startswith(" "):
            break
    return [r for r in rows if r.split()[0] == "REC"]


joined = recorder_rows()
apart_rows = recorder_rows("--apart", two)
check("without the switch the two blocks stand in one row",
      len(joined) == 1, "%d rows: %s" % (len(joined), joined))
check("with the switch they stand in two",
      len(apart_rows) == 2, "%d rows: %s" % (len(apart_rows), apart_rows))
check("so the switch changes the plan at all",
      joined != apart_rows,
      "with and without came out the same: %s" % joined)

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
