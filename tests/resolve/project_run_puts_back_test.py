# -*- coding: utf-8 -*-
"""A run that never tidied up leaves nothing, and what it remembers comes back.

Against a DaVinci Resolve that is really running. Every test deletes its
own project in a finally, and a finally does not run when the process is
killed -- so resolve.sh calls sweep.py before and after the tests. This is
the test of that, and it makes the bad case rather than waiting for it: a
child run makes its project, ends without deleting it, and leaves it
standing and open in front of somebody, exactly as a killed one does.

In order -- what the run remembers is a project it can open again; a
project Resolve has only created and never saved stands in no project
list, a run asked to make one of its own beside it leaves itself out
instead and leaves it open and unsaved where it was, it is therefore
remembered as nothing, and the sweep is content without it and asks for
nothing by hand; a decoy stands beside the open project that only looks
like the tests' own, and a folder that has their whole shape;
a run that never tidied up leaves its project behind and
open; the sweep takes that project and that folder and says which, leaves
the decoy standing, and opens the project that was open at the start
again and names it; and last, everything this test made is gone again.
The decoy is the narrowness: it carries the vpm-test prefix and not the
whole shape, so a pattern loose enough to hit somebody's own project hits
it first.

The limit of the method: nothing is killed here. Killing a run that is
holding a connection to Resolve takes Resolve down, and a run cannot
reliably let go of that connection first -- both measured, and the
numbers stand beside the child below. So what stands in for the accident
is a run that simply never deletes what it made. The leftover is
Resolve's own state and is the same either way.

And where the sweep would remember nothing of what is open -- a project
of the tests' own shape, or one that stands in no project list -- this
test leaves itself out. It could not put that state back afterwards, and
moving somebody's work without being able to put it back is worse than
checking nothing.

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


def which_says():
    """What the run would remember, asked the way resolve.sh asks it.

    Standard output only, as resolve.sh takes it -- a name with anything
    else glued to it would be a name nobody can load.
    """
    out = subprocess.run([sys.executable, os.path.join(HERE, "sweep.py"),
                          "--which"], capture_output=True, text=True)
    return out.stdout.strip(), out.returncode


def swept_and_restored(name):
    """The sweep resolve.sh runs at the end, with what --which answered."""
    out = subprocess.run([sys.executable, os.path.join(HERE, "sweep.py"),
                          "--sweep", "--restore", name],
                         capture_output=True, text=True)
    return out.stdout + out.stderr, out.returncode


# What the first child does: the two steps every one of these tests takes
# before it checks anything -- connect, and ask OwnProject for a project of
# its own. Nothing after that, and nothing tidied up, because the point of
# it is that nothing may be made: it runs while the decoy above is open and
# unsaved, and a project made now would take that decoy away for good.
#
# A child rather than a call in this process, and not for honesty's sake:
# leaving out prints SKIPPED: at the start of a line, and resolve.sh reads
# that off this test's own output before it looks at anything else. Called
# here, the one line would turn the whole file into a test that left itself
# out, whatever every check in it had said. It is also cheap, because it
# stops before the one expensive step -- measured on 1.9.2026 against
# Resolve 21.0.4.5: three runs at 0.10, 0.08 and 0.08 s, against 1.2 to 1.4
# for the child below that really makes one.
OPENS_ONE = '''
import sys
sys.path.insert(0, %r)
import resolve_ground as g

vpm = g.program()
resolve = vpm.connect_to_resolve()
own = g.OwnProject(vpm, resolve, "guard")
own.open()
print("it made %%s" %% own.name)
'''

# What the second child does: make a project the way any test does, say so,
# and end. It never deletes it and it has no finally -- the project left
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

# Asked before anything is made: where the sweep remembers nothing there
# is nothing to put back at the end, and a test that cannot put back what
# it moved has no business moving it.
before, which_rc = which_says()
if which_rc != 0:
    ground_of.leave_out("sweep.py --which ended with %d and said %r -- there "
                        "is no Resolve to ask" % (which_rc, before))
if not before:
    ground_of.leave_out(
        "the sweep remembers nothing of what is open. Resolve is on %r, "
        "which is either a project of the tests' own shape or one that "
        "stands in no project list -- nothing here could be put back "
        "afterwards. Open a project of your own in Resolve, or save the one "
        "that is open, and run again." % open_now(pm))

work = tempfile.mkdtemp(prefix="vpm_back_")
# A name that carries the tests' prefix and not their shape: no process
# id, no four hexadecimal digits. Anything looser than the whole shape
# takes it, which is the point of it.
decoy = "vpm-test-decoy-KEEP-%d" % os.getpid()
# And a folder that does have the whole shape. A run that died half way
# through leaves one, and a folder stands in no project list -- so this is
# made outright rather than by taking Resolve down to get it.
folder = ground_of.a_test_name("folder")
child = None
made_decoy = False
made_folder = False
try:
    print("\n1. What the run remembers is a project it can open again")
    check("what the run remembers is a project it can open again",
          before in listed(pm),
          "--which said %r, among %d projects: %s"
          % (before, len(listed(pm)), before in listed(pm)))

    print("\n2. A project in no project list is remembered as nothing")
    made_decoy = pm.CreateProject(decoy) is not None
    # Left unsaved on purpose, and that is the whole state. Measured on
    # Resolve 21.0.4.5 on 1.9.2026: a project that was only created stays
    # out of the project list for as long as it is the open one, and
    # LoadProject cannot fetch back a name that is not in that list.
    check("a project that was never saved is in no project list",
          made_decoy and decoy not in listed(pm),
          "%r among %d projects: %s"
          % (decoy, len(listed(pm)), decoy in listed(pm)))
    # And that state is the one a run must not walk into. Read the way
    # resolve.sh reads it: the return code, and SKIPPED: at the start of a
    # line of its own -- a bow-out that says neither is one nobody counts.
    ran = subprocess.run([sys.executable, "-c", OPENS_ONE % HERE],
                         capture_output=True, text=True)
    loud = [line for line in ran.stdout.splitlines()
            if line.startswith("SKIPPED:")]
    check("a test does not make a project while an unsaved one is open",
          ran.returncode == 2 and len(loud) == 1,
          "OwnProject.open() ended with %d and put SKIPPED at the start of "
          "%d lines; it said %r, and %r on the error stream"
          % (ran.returncode, len(loud), ran.stdout.strip()[:70],
             ran.stderr.strip()[-70:]))
    # The return code says it bowed out; this says it bowed out in time.
    # A guard that ran after the creating would answer 2 just the same and
    # the decoy would be gone.
    check("and the unsaved project is still open and still unsaved",
          open_now(pm) == decoy and decoy not in listed(pm),
          "Resolve has %r open, the decoy is %r and among %d projects: %s"
          % (open_now(pm), decoy, len(listed(pm)), decoy in listed(pm)))
    said_which, rc_which = which_says()
    check("a project in no project list is not reported as open",
          said_which == "",
          "--which said %r (ended with %d) while Resolve had %r open"
          % (said_which, rc_which, open_now(pm)))
    # And the rest of the way bears the empty answer: what --which said is
    # what resolve.sh hands to --restore, whatever it said.
    said_empty, rc_empty = swept_and_restored(said_which)
    print(said_empty.rstrip())
    check("the sweep is content where there was nothing to put back",
          rc_empty == 0,
          "sweep.py --restore %r ended with %d" % (said_which, rc_empty))
    check("and it does not ask for a project to be opened by hand",
          "WOULD NOT OPEN" not in said_empty,
          "'WOULD NOT OPEN' in what the sweep printed: %s, of %d characters"
          % ("WOULD NOT OPEN" in said_empty, len(said_empty)))
    # From here on the decoy is a project like any other: saved, in the
    # list, and left standing while the sweep runs over everything else.
    pm.SaveProject()
    pm.LoadProject(before)

    print("\n3. A decoy and a folder stand beside the open project")
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

    print("\n4. A run ends without tidying up, so nothing of its own is put back")
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

    print("\n5. The sweep clears it away and puts the project back")
    said = swept_and_restored(before)[0]
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
        if open_now(pm) != before:
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
        if open_now(pm) != before:
            pm.LoadProject(before)
        if open_now(pm) != before:
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
