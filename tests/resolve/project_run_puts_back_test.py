# -*- coding: utf-8 -*-
"""A killed run leaves nothing, and what was open is open again.

Against a DaVinci Resolve that is really running. Every test deletes its
own project in a finally, and a finally does not run when the process is
killed -- so resolve.sh calls sweep.py before and after the tests. This is
the test of that, and it makes the bad case rather than waiting for it: a
child run is started, left until it has really made its project, and then
killed outright, so nothing of its own can tidy up.

In order -- a project is open and a decoy is put beside it that only looks
like the tests' own, a killed run leaves its project behind and open, the
sweep deletes that one and says which, the decoy is left standing, and the
project that was open at the start is open again and named. The decoy is
the narrowness: it carries the vpm-test prefix and not the whole shape,
so a pattern loose enough to hit somebody's own project hits it first.

This one must not run beside the others: its own tidying up sweeps every
project of the tests' shape, and theirs would go with it. resolve.sh runs
them one after another, which is what that is for.

A step that throws is a failed judgement and not a traceback, so the
closing count is reached whatever happens.
"""
import os
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import resolve_ground as ground_of

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def listed(pm):
    return pm.GetProjectListInCurrentFolder() or []


def open_now(pm):
    p = pm.GetCurrentProject()
    return p.GetName() if p else ""


# What the child does: make a project the way any test does, say so, and
# then wait to be killed. It writes each step, so the parent waits on
# something that only moves because the child is working.
CHILD = '''
import os, sys, time
sys.path.insert(0, %r)
import resolve_ground as g

WHERE = %r


def step(text):
    part = WHERE + ".part"
    with open(part, "w") as f:
        f.write(text)
    os.replace(part, WHERE)


step("started")
vpm = g.program()
step("program loaded")
resolve = vpm.connect_to_resolve()
step("connected")
ground = g.OwnProject(vpm, resolve, "killed")
ground.open()
step("project " + ground.name)
while True:
    time.sleep(0.5)
'''

vpm = ground_of.program()
resolve = ground_of.a_resolve(vpm)
print("Resolve: %s %s" % (resolve.GetProductName(), resolve.GetVersionString()))
pm = resolve.GetProjectManager()

work = tempfile.mkdtemp(prefix="vpm_back_")
# A name that carries the tests' prefix and not their shape: no process
# id, no four hexadecimal digits. Anything looser than the whole shape
# takes it, which is the point of it.
decoy = "vpm-test-decoy-KEEP-%d" % os.getpid()
before = open_now(pm)
child = None
made_decoy = False
try:
    print("\n1. A project is open, and a decoy stands beside it")
    check("a project was open when the run started",
          bool(before), "Resolve had %r open" % before)
    made_decoy = pm.CreateProject(decoy) is not None
    pm.SaveProject()
    if before:
        pm.LoadProject(before)
    check("the decoy is in the project list to begin with",
          decoy in listed(pm),
          "%r among %d projects" % (decoy, len(listed(pm))))
    check("and the decoy does not have the shape the sweep deletes",
          not ground_of.TEST_PROJECT.match(decoy),
          "%r against %s" % (decoy, ground_of.TEST_PROJECT.pattern))

    print("\n2. A run is killed outright, so nothing of its own tidies up")
    told = os.path.join(work, "how_far")
    script = os.path.join(work, "child.py")
    with open(script, "w") as f:
        f.write(CHILD % (HERE, told))
    log = open(os.path.join(work, "child.log"), "w")
    child = subprocess.Popen([sys.executable, script], stdout=log,
                             stderr=subprocess.STDOUT)

    def how_far():
        try:
            with open(told) as f:
                return f.read()
        except (IOError, OSError):
            return ""

    arrived, seen, waited = ground_of.progresses(
        how_far, lambda x: x.startswith("project "))
    check("the killed run got as far as making its project",
          arrived, "it got to %r after %.1f s" % (seen, waited))
    killed = seen[len("project "):] if arrived else ""
    child.kill()
    child.wait()
    child = None
    check("a run that was killed leaves its project behind",
          bool(killed) and killed in listed(pm),
          "%r among %d projects" % (killed, len(listed(pm))))
    check("and it leaves that project open in front of somebody",
          bool(killed) and open_now(pm) == killed,
          "Resolve has %r open, the killed run made %r"
          % (open_now(pm), killed))

    print("\n3. The sweep clears it away and puts the project back")
    swept = subprocess.run(
        [sys.executable, os.path.join(HERE, "sweep.py"), "--sweep",
         "--restore", before], capture_output=True, text=True)
    said = swept.stdout + swept.stderr
    print(said.rstrip())
    check("the sweep deletes what the killed run left behind",
          bool(killed) and killed not in listed(pm),
          "%r in the list: %s, of %d projects"
          % (killed, killed in listed(pm), len(listed(pm))))
    check("and it says by name which project it deleted",
          bool(killed) and killed in said,
          "%r in what the sweep printed: %s" % (killed, killed in said))
    check("a project that only looks like the tests' own is left alone",
          decoy in listed(pm),
          "%r in the list: %s, of %d projects"
          % (decoy, decoy in listed(pm), len(listed(pm))))
    check("the project that was open at the start is open again",
          open_now(pm) == before,
          "Resolve has %r open, it started with %r" % (open_now(pm), before))
    check("and the sweep says by name which project it opened",
          before in said,
          "%r in what the sweep printed: %s" % (before, before in said))
except Exception as e:
    import traceback
    traceback.print_exc()
    check("the run reached the end without an exception", False,
          "%s: %s" % (type(e).__name__, str(e).replace("\n", " ")[:120]))
finally:
    left_over = []
    try:
        if child is not None:
            child.kill()
            child.wait()
    except Exception as e:
        left_over.append("the child would not die: %s" % e)
    try:
        if before and open_now(pm) != before:
            pm.LoadProject(before)
        if made_decoy:
            pm.DeleteProject(decoy)
            if decoy in listed(pm):
                left_over.append("%r is still in the project list" % decoy)
        # And whatever this test made under the tests' own shape.
        gone, stayed = ground_of.swept(pm)
        if stayed:
            left_over.append("still there: %s" % ", ".join(stayed))
        if before and open_now(pm) != before:
            pm.LoadProject(before)
        if before and open_now(pm) != before:
            left_over.append("%r could not be opened again" % before)
    except Exception as e:
        left_over.append("could not tidy up: %s" % e)
    import shutil
    shutil.rmtree(work, ignore_errors=True)

check("everything the test made is gone again",
      not left_over, "; ".join(left_over) or "the decoy and the child are gone")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
