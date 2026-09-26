# -*- coding: utf-8 -*-
"""Each camera's colour row in the metrics is measured on its own file.

A line run on way_ground's production, in a child whose thread pool is
stood in: every camera is written as usual, but the pool hands them
back last one first, so completion order is the reverse of file order
every time. First that the reversal happened and the files can be told
apart; then each camera's brightness in the metrics CSV against its own
written file, and the RESULT list in the order the cameras were given.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import csv
import json
import tempfile
import time
import the_program
import way_ground as ground

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

# The child: the program loaded as the tests load it, the pool of the
# camera stage stood in so it answers last-submitted first, then main.
CHILD = r'''
import json, sys
sys.path.insert(0, sys.argv.pop(1))
log = sys.argv.pop(1)
import the_program
vpm = the_program.load()
real = vpm.futures


class Reversed(object):
    """The real pool, handing its jobs back in reverse submission order."""
    ThreadPoolExecutor = real.ThreadPoolExecutor

    @staticmethod
    def as_completed(jobs):
        """Wait for all, then yield the last submitted first."""
        jobs = list(jobs)
        real.wait(jobs)
        with open(log, "w") as f:
            json.dump([jobs.index(j) for j in reversed(jobs)], f)
        return iter(reversed(jobs))


vpm.distribute_tracks_to_cameras.__globals__["futures"] = Reversed
sys.argv[0] = the_program.SCRIPT
sys.exit(vpm.main())
'''

vpm = the_program.load()
vpm.set_language("en")
work = tempfile.mkdtemp(prefix="vpm_colour_own_")
store = tempfile.mkdtemp(prefix="vpm_colour_store_")
child = os.path.join(work, "reversed_pool.py")
with open(child, "w") as f:
    f.write(CHILD)
log = os.path.join(work, "order.json")
out = os.path.join(work, "out")
argv = ground.line(child, ground.separation_file(vpm, work), out)
argv[2:2] = [HERE, log]
code, said, stuck = ground.line_run(argv, store)
if code != 0 or stuck:
    check("the line run with the pool stood in ends in 0", False,
          "code %s, stuck %s, last lines: %s"
          % (code, stuck, " / ".join(said.strip().splitlines()[-4:])))
    stop()

# --------------------------------------------------- the ground holds
print("1. The cameras finished last one first, and can be told apart")
try:
    with open(log) as f:
        order = json.load(f)
except (OSError, ValueError):
    order = None
check("the camera stage handed its files back in reverse order",
      order == [2, 1, 0], "handed back in submission places %r" % order)
written = {}
for cam in (ground.GUEST, ground.PRES, ground.WIDE):
    level = vpm.measure_picture_levels(os.path.join(out, cam + "_audio.mov"))
    written[cam] = round(level["y"], 1) if level else None
levels = sorted(v for v in written.values() if v is not None)
check("the three written camera files measure apart in brightness",
      len(set(levels)) == 3,
      "brightness of the written files: %r" % written)

# ----------------------------------------------- the rows against them
print("\n2. Each metrics row is its own camera's, the RESULT in file order")
rows = {}
path = os.path.join(out, "%s_metrics.csv" % ground.PRODUCTION)
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) > 3 and row[0].startswith("Colour ") \
                    and row[1] == "Brightness":
                rows[row[0][len("Colour "):]] = float(row[3])
check("each camera's brightness row is measured on its own file",
      rows == written, "metrics %r against the files %r" % (rows, written))
listed = []
head = vpm.T('\nRESULT').strip()
lines = said.splitlines()
if head in lines:
    for line in lines[lines.index(head) + 1:]:
        if not line.startswith("  "):
            break
        if line.endswith("_audio.mov"):
            listed.append(os.path.basename(line.strip()))
check("the RESULT lists the cameras in the order they were given",
      listed == [ground.GUEST + "_audio.mov", ground.PRES + "_audio.mov",
                 ground.WIDE + "_audio.mov"],
      "listed %r" % listed)
stop()
