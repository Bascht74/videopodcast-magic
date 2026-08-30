# -*- coding: utf-8 -*-
"""The bar neither falls back nor stands still.

On a long run the bar is the only sign that anything moves. Opening a
project fills it with the measuring; pressing Start in that moment used
to add the run's stages on top, so the bar opened high and fell back. A
bar that never falls then made it stand still instead. This is
arithmetic, and can be held against numbers without a window.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

bad = []


def check(what, ok, detail=""):
    print("  %-58s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


def measuring_still_going():
    """The state a project leaves behind: one step done, one running."""
    plan = vpm.ProgressPlan()
    plan.add("measuring", 1.0)
    plan.add("probing", 1.0)
    plan.begin("measuring")
    plan.done("measuring")
    plan.begin("probing")
    return plan


RUN = ("tracks", "render", "resolve", "write")

print("1. Start pressed while the measuring is still going")
plan = measuring_still_going()
check("the bar stands where the measuring left it",
      abs(plan.total() - 0.5) < 1e-9, "%.3f" % plan.total())
plan.clear()
for name in RUN:
    plan.add(name, 1.0)
check("clearing puts it back to nothing", abs(plan.total()) < 1e-9,
      "%.3f" % plan.total())
seen = []
for i, name in enumerate(RUN, 1):
    plan.begin(name)
    plan.done(name)
    seen.append((plan.total(), i / float(len(RUN))))
check("and from there it says the truth at every step",
      all(abs(a - b) < 1e-9 for a, b in seen),
      "; ".join("%.3f vs %.3f" % (a, b) for a, b in seen))

print("\n2. What it did before, kept as a number")
# The counter-proof, read out rather than remembered: without the
# clearing the bar stands still through the stage left over from the
# measuring and the first of the four that follow it.
plan = measuring_still_going()
# Asking is what sets the high mark: total() keeps the largest figure
# it has ever been asked for. A test that does not ask measures
# something else.
plan.total()
for name in RUN:
    plan.add(name, 1.0)
held = []
for i, name in enumerate(("probing",) + RUN, 2):
    plan.begin(name)
    plan.done(name)
    held.append(round(plan.total(), 3))
check("without it, the bar stands still for two stages",
      held[:2] == [0.5, 0.5], str(held))
check("and only then does it move again",
      held[2] > 0.5, str(held))

print("\n3. It never goes backwards, whatever happens")
# The older guard is still in force, and it has to be: a step that
# reports itself smaller than it was would otherwise pull the bar down.
plan = vpm.ProgressPlan()
plan.add("one", 1.0)
plan.report("one", 0.8)
was = plan.total()
plan.report("one", 0.2)
check("a step reporting itself smaller does not pull it down",
      plan.total() >= was - 1e-9, "%.3f after %.3f" % (plan.total(), was))
# And adding work later cannot either.
plan.add("two", 1.0)
check("nor does work announced later",
      plan.total() >= was - 1e-9, "%.3f after %.3f" % (plan.total(), was))

print("\n4. A step nobody announced still counts")
# What makes the clearing safe: a step that was thrown away puts
# itself back when it reports, so nothing still to come is lost.
plan = vpm.ProgressPlan()
plan.add("one", 1.0)
plan.done("stranger")
check("reporting an unknown step adds it", "stranger" in plan.order,
      str(plan.order))
check("and it is counted in the whole", abs(plan.total() - 0.5) < 1e-9,
      "%.3f" % plan.total())

# --------------------------------------------- The names on both paths
# One bar draws both paths, so both must call their stages the same. A
# stage announced but never listed lowers every share already reported;
# one listed but never announced is skipped in a jump.
print("\n5. The stages have one set of names")
import re
source = open(SCRIPT, encoding="utf-8").read()
said = set(re.findall(r'step_begin\(\s*"([^"]+)"', source))
planned = set()
for multitrack in (False, True):
    for cameras in (0, 2):
        for auphonic in (False, True):
            for speakers in (False, True):
                planned |= set(name for name, _w, _c in vpm.run_stages(
                    multitrack, cameras, auphonic, speakers))
check("every stage the run announces is one the plan knows",
      said <= planned, str(sorted(said - planned)))
# The other way round is not an error in general, but a stage nobody
# ever announces would be dead weight in the bar.
check("and the plan lists nothing nobody ever reaches",
      planned <= said, str(sorted(planned - said)))
# The simple path aligns against the cameras but does not pull their
# audio out, so listing that stage for it would hold the bar back.
check("no camera-audio stage on the simple path",
      "camera audio" not in [n for n, _w, _c in
                             vpm.run_stages(False, 2, False, False)],
      str([n for n, _w, _c in vpm.run_stages(False, 2, False, False)]))
check("but there is one on the multitrack path",
      "camera audio" in [n for n, _w, _c in
                         vpm.run_stages(True, 2, False, False)])

print("\n%s" % ("ALL OK" if not bad else "FAIL: " + ", ".join(bad)))
sys.exit(1 if bad else 0)
