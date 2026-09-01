# -*- coding: utf-8 -*-
"""A run that never tidied up leaves nothing, and what was open is open again.

Against a DaVinci Resolve that is really running. Every test deletes its
own project in a finally, and a finally does not run when the process is
killed -- so resolve.sh calls sweep.py before and after the tests. This is
the test of that, and it makes the bad case rather than waiting for it: a
child run makes its project, ends without deleting it, and leaves it
standing and open in front of somebody, exactly as a killed one does.

In order -- a project is open, a decoy stands beside it that only looks
like the tests' own and a folder that has their whole shape, a run that
never tidied up leaves its project behind and open, the sweep takes that
project and that folder and says which, the decoy is left standing, and
the project that was open at the start is open again and named. The decoy
is the narrowness: it carries the vpm-test prefix and not the whole
shape, so a pattern loose enough to hit somebody's own project hits it
first.

The limit of the method: nothing is killed here. Killing a run that is
holding a connection to Resolve takes Resolve down, and a run cannot
reliably let go of that connection first -- both measured, and the
numbers stand beside the child below. So what stands in for the accident
is a run that simply never deletes what it made. The leftover is
Resolve's own state and is the same either way.

This one must not run beside the others: its own tidying up sweeps every
project of the tests' shape, and theirs would go with it. resolve.sh runs
them one after another, which is what that is for.

A step that throws is a failed judgement and not a traceback, so the
closing count is reached whatever happens.
"""
import os
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


def folders(pm):
    return pm.GetFolderListInCurrentFolder() or []


def open_now(pm):
    p = pm.GetCurrentProject()
    return p.GetName() if p else ""


# What the child does: make a project the way any test does, say so, and
# end. It never deletes it and it has no finally -- the project left
# standing and open is the whole point of it. It writes each step, so the
# parent waits on something that only moves because the child is working.
#
# It used to be killed here instead, and that took Resolve down. Measured
# on 1.9.2026 against Resolve 21.0.4.5: three killed runs in a row needed
# 1.4 s, 1.4 s and then 9.0 s to make their project -- the third was
# already labouring before the signal -- and Resolve was gone afterwards,
# leaving a half-finished project that the project manager shows as a
# folder. Letting go of the connection before the signal does not save it
# either: in four of six tries the process still held one after dropping
# every reference and both modules, and nothing inside Python can see
# them (gc.get_objects() answers 0 while the socket is open). Ending by
# itself costs nothing: three such runs in a row stayed at 1.2, 1.2 and
# 1.4 s, and the project was left standing and open every time.
CHILD = '''
import os, sys
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
ground = g.OwnProject(vpm, resolve, "left")
ground.open()
step("project " + ground.name)
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
# And a folder that does have the whole shape. A run that died half way
# through leaves one, and a folder stands in no project list -- so this is
# made outright rather than by taking Resolve down to get it.
folder = ground_of.a_test_name("folder")
before = open_now(pm)
child = None
made_decoy = False
made_folder = False
try:
    print("\n1. A project is open, and a decoy and a folder stand beside it")
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
    made_folder = bool(pm.CreateFolder(folder))
    check("a folder of the tests' shape is in the folder list to begin with",
          folder in folders(pm),
          "%r among %d folders" % (folder, len(folders(pm))))

    print("\n2. A run ends without tidying up, so nothing of its own is put back")
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
    check("the run got as far as making its project",
          arrived, "it got to %r after %.1f s" % (seen, waited))
    left_behind = seen[len("project "):] if arrived else ""
    # On its own feet, or the leftover was made the way that took Resolve
    # down. Waiting on the process, giving up when it stops moving.
    ended, code, out_after = ground_of.progresses(
        child.poll, lambda x: x is not None)
    if ended:
        child = None
    check("the run ended by itself, nothing had to be killed",
          ended and code == 0,
          "it ended with %r after %.1f s" % (code, out_after))
    check("a run that never tidied up leaves its project behind",
          bool(left_behind) and left_behind in listed(pm),
          "%r among %d projects" % (left_behind, len(listed(pm))))
    check("and it leaves that project open in front of somebody",
          bool(left_behind) and open_now(pm) == left_behind,
          "Resolve has %r open, the run made %r"
          % (open_now(pm), left_behind))

    print("\n3. The sweep clears it away and puts the project back")
    swept = subprocess.run(
        [sys.executable, os.path.join(HERE, "sweep.py"), "--sweep",
         "--restore", before], capture_output=True, text=True)
    said = swept.stdout + swept.stderr
    print(said.rstrip())
    check("the sweep deletes what that run left behind",
          bool(left_behind) and left_behind not in listed(pm),
          "%r in the list: %s, of %d projects"
          % (left_behind, left_behind in listed(pm), len(listed(pm))))
    check("and it says by name which project it deleted",
          bool(left_behind) and left_behind in said,
          "%r in what the sweep printed: %s"
          % (left_behind, left_behind in said))
    check("the sweep deletes a folder of the tests' shape as well",
          made_folder and folder not in folders(pm),
          "%r in the folder list: %s, of %d folders"
          % (folder, folder in folders(pm), len(folders(pm))))
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
        if made_folder and folder in folders(pm):
            pm.DeleteFolder(folder)
            if folder in folders(pm):
                left_over.append("%r is still in the folder list" % folder)
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
      not left_over, "; ".join(left_over) or "the decoy, the folder and the "
      "child are gone")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
