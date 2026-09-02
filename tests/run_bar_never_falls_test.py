# -*- coding: utf-8 -*-
"""The bar neither falls back nor stands still.

On a long run the bar is the only sign that anything moves. Opening a
project fills it with the measuring; pressing Start in that moment used
to add the run's stages on top, so the bar opened high and fell back. A
bar that never falls then made it stand still instead. Between two
figures only the creeping moves it, so that is held here too, and last
the stages having one set of names. This is arithmetic, no window.

What is asked is always the bar, never a step's own figure -- that is
the neighbour's subject. And it is asked in between as seldom as it
can be: the bar keeps a high mark, so a judgement that has just raised
it can no longer see anything fall.

The limit of the last part: which stages the run announces is read off
the program's own calls, so a name written out or held in a constant is
seen and one built at run time is not -- the line says which.
"""
import ast, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
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
# The bar is not asked between the two figures. Asked once, its high
# mark would hold the answer up by itself and this would test nothing;
# so what is wanted is written out instead -- one step of weight one,
# best figure 0.8, and the bar is that.
plan = vpm.ProgressPlan()
plan.add("one", 1.0)
plan.report("one", 0.8)
plan.report("one", 0.2)
check("a step's smaller second figure never reaches the bar",
      abs(plan.total() - 0.8) < 1e-9, "%.3f, wanted 0.800" % plan.total())
# Work announced later is the high mark's own case: there the sum
# really does fall, from 0.8 to 0.4, and only the mark holds it up.
plan = vpm.ProgressPlan()
plan.add("one", 1.0)
plan.report("one", 0.8)
was = plan.total()
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

# ------------------------------------------- Between two figures, only
# the creeping moves the bar. Pulling the audio out of an hour of 4K
# reports nothing for minutes; if the bar reads reported figures alone
# it stands still for all of them, and a bar that stands still is what
# this file is against. Nothing below names a number out of creep's
# own settings -- each judgement asks only whether it moved.
print("\n5. Between two figures the creeping moves it")
plan = vpm.ProgressPlan()
plan.begin("slow")
still = plan.total()
plan.creep(30.0)
check("a step that reports nothing still moves the bar",
      plan.total() > still, "%.3f after %.3f" % (plan.total(), still))
# A figure arriving late is a floor, not a ceiling: the step crept past
# it while nobody was asking, and that is not thrown away. Two plans
# crept side by side, one of them told a small figure at the end.
crept = vpm.ProgressPlan()
late = vpm.ProgressPlan()
crept.begin("slow")
late.begin("slow")
for _ in range(100):
    crept.creep(60.0)
    late.creep(60.0)
late.report("slow", 0.1)
check("a small figure arriving late does not undo the creeping",
      late.total() >= crept.total() - 1e-9,
      "%.3f against %.3f" % (late.total(), crept.total()))
# And how far a step may creep hangs on its best figure, not its last.
# On the lower one the ceiling would sit under where the step already
# is, and the bar would freeze there.
plan = vpm.ProgressPlan()
plan.add("one", 1.0)
plan.report("one", 0.8)
plan.report("one", 0.2)
stood = plan.total()
for _ in range(20):
    plan.creep(60.0)
check("and the best figure, not the last, sets how far it creeps",
      plan.total() > stood, "%.3f after %.3f" % (plan.total(), stood))

# --------------------------------------------- The names on both paths
# One bar draws both paths, so both must call their stages the same. A
# stage announced but never listed lowers every share already reported;
# one listed but never announced is skipped in a jump.
print("\n6. The stages have one set of names")
# The announcements are collected from the program's own calls, not from
# the text around them: a name written out is read off the call, a name
# held in a constant is asked of the program. Reading the text alone saw
# only written-out names, so moving one single stage name into a
# constant -- a change that alters nothing the program does -- made this
# section red. What still cannot be read, a name built at run time or
# taken out of a loop, is collected apart and named in the line.
said = set()
unread = []
for node in ast.walk(ast.parse(open(SCRIPT, encoding="utf-8").read())):
    if not (isinstance(node, ast.Call) and node.args
            and getattr(node.func, "id", "") == "step_begin"):
        continue
    what = node.args[0]
    if isinstance(what, ast.Constant) and isinstance(what.value, str):
        said.add(what.value)
    elif isinstance(what, ast.Name) and isinstance(
            getattr(vpm, what.id, None), str):
        said.add(getattr(vpm, what.id))
    else:
        unread.append("line %d" % what.lineno)
aside = "" if not unread else "; announcements not read as a name: %s" % (
    ", ".join(unread))
planned = set()
for multitrack in (False, True):
    for cameras in (0, 2):
        for auphonic in (False, True):
            for speakers in (False, True):
                planned |= set(name for name, _w, _c in vpm.run_stages(
                    multitrack, cameras, auphonic, speakers))
check("every stage the run announces is one the plan knows",
      said <= planned, str(sorted(said - planned)) + aside)
# The other way round is not a fault in general, but a stage nobody
# ever announces would be dead weight in the bar.
check("and the plan lists nothing nobody ever reaches",
      planned <= said, str(sorted(planned - said)) + aside)
# The simple path aligns against the cameras but does not pull their
# audio out, so listing that stage for it would hold the bar back.
check("no camera-audio stage on the simple path",
      "camera audio" not in [n for n, _w, _c in
                             vpm.run_stages(False, 2, False, False)],
      str([n for n, _w, _c in vpm.run_stages(False, 2, False, False)]))
multitrack = [n for n, _w, _c in vpm.run_stages(True, 2, False, False)]
check("but there is one on the multitrack path",
      "camera audio" in multitrack,
      "%d stages on that path: %s" % (len(multitrack), multitrack))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
