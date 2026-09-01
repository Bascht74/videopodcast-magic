"""The one bar: weights, creeping, and never going backwards."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, time
began = time.time()
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))

print("1. Long work takes up more of the bar")
p = vpm.ProgressPlan()
p.add("camera", 8.0)
p.add("wav", 1.0)
p.done("wav")
small = p.total()
p2 = vpm.ProgressPlan()
p2.add("camera", 8.0)
p2.add("wav", 1.0)
p2.done("camera")
big = p2.total()
check("the short one hardly moves it", small < 0.15, round(small, 3))
check("the long one moves it a lot", big > 0.85, round(big, 3))
check("both together are the whole thing",
      abs(small + big - 1.0) < 1e-9,
      "%.6f + %.6f = %.6f, wanted 1.0" % (small, big, small + big))

print("\n2. It does not go backwards")
p = vpm.ProgressPlan()
p.add("a", 1.0)
p.done("a")
was = p.total()
p.add("b", 1.0)          # a second step turns up while it runs
p.add("c", 1.0)
check("a step added later does not push it back", p.total() >= was,
      "%.3f -> %.3f" % (was, p.total()))
p.report("b", 0.5)
p.report("b", 0.2)       # a late, lower figure
check("a lower report is ignored", p.share["b"] == 0.5, p.share["b"])

print("\n3. A step with no figure creeps, but not past its end")
p = vpm.ProgressPlan()
p.add("slow", 1.0)
p.begin("slow")
p.creep(20.0)
one = p.share["slow"]
p.creep(20.0)
two = p.share["slow"]
for _ in range(200):
    p.creep(60.0)
far = p.share["slow"]
check("it moves", one > 0.2, round(one, 3))
check("and keeps moving", two > one, "%.3f -> %.3f" % (one, two))
check("it slows at the band", one > 0.2 and far > 0.93, round(far, 4))
check("and crawls on past it", far > 0.93 and far < 0.995, round(far, 4))
creeping = p.busy()
check("so it never says done by itself", creeping,
      "busy %r at a share of %.5f, wanted True" % (creeping, far))

q = vpm.ProgressPlan()
q.begin("fresh")
q.creep(30.0)
fast = q.share["fresh"]
r = vpm.ProgressPlan()
r.begin("old")
for _ in range(200):
    r.creep(30.0)
    if r.share["old"] >= 0.93:
        break
at_band = r.share["old"]
r.creep(30.0)
slow = r.share["old"] - at_band
check("the band is crossed", at_band >= 0.93, round(at_band, 4))
check("past it a step still moves", slow > 0, round(slow, 5))
check("but only a fraction of a step before it",
      slow < fast / 10.0, "%.5f against %.5f" % (slow, fast))
for _ in range(500):
    r.creep(60.0)
check("and it stops short of the very end", r.share["old"] < 0.9905,
      round(r.share["old"], 5))

print("\n4. A real figure beats the creep")
p = vpm.ProgressPlan()
p.report("x", 0.0)
p.creep(30.0)
crept = p.share["x"]
p.report("x", 0.99)
check("a real figure above the creep wins", p.share["x"] == 0.99,
      "crept to %.3f" % crept)

print("\n5b. A step that reports stays near what it reported")
p = vpm.ProgressPlan()
p.report("measured", 0.20)
for _ in range(100):
    p.creep(60.0)
check("it creeps a little past its figure", p.share["measured"] > 0.25,
      round(p.share["measured"], 3))
check("but not far past it", p.share["measured"] < 0.34,
      round(p.share["measured"], 3))
p.report("measured", 0.60)
for _ in range(100):
    p.creep(60.0)
check("the next figure carries it along", p.share["measured"] > 0.65,
      round(p.share["measured"], 3))
check("and it still stays close", p.share["measured"] < 0.74,
      round(p.share["measured"], 3))

print("\n5. Only what has started creeps")
p = vpm.ProgressPlan()
p.add("waiting", 1.0)
p.begin("under way")
p.creep(60.0)
check("an announced step stays at zero", p.share["waiting"] == 0.0,
      "waiting stands at %.5f, wanted 0.0" % p.share["waiting"])
check("a started one has moved", p.share["under way"] > 0.0,
      "under way stands at %.5f, wanted above 0.0" % p.share["under way"])

print("\n6. What it says while it works")
p = vpm.ProgressPlan()
p.report("one", 0.3, "Guest.mov")
check("one step: its own caption", p.line() == "Guest.mov", p.line())
p.report("two", 0.1, "WideCam.mov")
check("two steps: the first and a count",
      p.line() == vpm.T('%s and %d more') % ("Guest.mov", 1), p.line())
p.done("one"); p.done("two")
check("nothing running: no line", p.line() == "", repr(p.line()))
left = p.busy()
check("and nothing outstanding", not left, "busy %r, wanted False" % (left,))
whole = p.total()
check("the bar stands at the end", abs(whole - 1.0) < 1e-9,
      "the bar stands at %.9f, wanted 1.0" % whole)

print("\n7. An empty plan says nothing and does not divide by zero")
p = vpm.ProgressPlan()
bare_total, bare_busy, bare_line = p.total(), p.busy(), p.line()
check("total is zero", bare_total == 0.0,
      "total %r, wanted 0.0" % (bare_total,))
check("not busy", not bare_busy, "busy %r, wanted False" % (bare_busy,))
check("no line", bare_line == "",
      "line %r, wanted %r" % (bare_line, ""))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
