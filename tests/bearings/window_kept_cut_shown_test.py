# -*- coding: utf-8 -*-
"""The preview shows a handover a run kept for what is set now.

A dry run keeps its handover in the stage store under a key of what it
was worked from -- its line, its plan, its files; the preview reads
that one first, and the file a run wrote otherwise. In order: which is read,
and when the preview counts as out of date -- a kept handover not yet
shown, one shown, the key moved on. The store lies in a cache folder
of the test's own; the handovers are stand-ins that carry only a word
saying where they came from and the axis they stood on.
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
import the_program
import json
import shutil
import tempfile
import time

WORK = tempfile.mkdtemp(prefix="vpm_keptcut_")
os.environ["VPM_CACHE"] = os.path.join(WORK, "cache")
vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


FILE = os.path.join(WORK, "Episode_resolve.json")
with open(FILE, "w", encoding="utf-8") as f:
    json.dump({"came_from": "the run's file"}, f)
KEY = vpm.stage_key("handover", (), axis="axis_1", in_out=[0.0, 60.0])
OTHER = vpm.stage_key("handover", (), axis="axis_1", in_out=[0.0, 61.0])
MOVED = vpm.stage_key("handover", (), axis="axis_2", in_out=[0.0, 60.0])
AXIS = vpm.stage_key("axis", (), material="these")
vpm.stage_put(KEY, {"came_from": "kept for this key", "axis_key": AXIS})
vpm.stage_put(MOVED, {"came_from": "kept for the next key",
                      "axis_key": AXIS})


def word(d):
    return (d or {}).get("came_from")


#------------------------------------------------------ which one is read

print("which handover the preview reads")
state = {"handover_key": KEY, "resolve_json": FILE,
         "axis_stage_key": AXIS}
got = word(vpm.preview_handover(state))
check("a handover kept for the key set now is what the preview reads",
      got == "kept for this key",
      "read %r, wanted 'kept for this key'" % got)
state_other = {"handover_key": OTHER, "resolve_json": FILE,
               "axis_stage_key": AXIS}
got = word(vpm.preview_handover(state_other))
check("with nothing kept under the key the run's file is read as before",
      got == "the run's file", "read %r, wanted 'the run's file'" % got)

#-------------------------------------------------------- when it is stale

print("\nwhen the preview is out of date")
before = {"handover_key": KEY, "resolve_json": FILE, "statistics": {"n": 1},
          "preview_from": vpm.handover_mark(FILE), "axis_stage_key": AXIS}
check("a kept handover not yet shown puts the preview out of date",
      vpm.preview_out_of_date(before) is True,
      "answered %r with the run's file shown" % vpm.preview_out_of_date(
          before))
state["statistics"] = {"n": 1}
check("one that is shown is not out of date again",
      vpm.preview_out_of_date(state) is False,
      "answered %r, shown from %r" % (vpm.preview_out_of_date(state),
                                      state.get("preview_from")))
state["handover_key"] = MOVED
check("a key moved on to another kept handover is out of date again",
      vpm.preview_out_of_date(state) is True,
      "answered %r, shown from %r" % (vpm.preview_out_of_date(state),
                                      state.get("preview_from")))

shutil.rmtree(WORK, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
