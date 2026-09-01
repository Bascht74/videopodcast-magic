# -*- coding: utf-8 -*-
"""The ground the Resolve tests stand on: the program, and a project of
their own that goes away again.

These tests talk to a DaVinci Resolve that is really running on this
machine, so they cannot go into the suite: on a machine without Resolve
every one of them would be red for a reason that is not a fault. They
live beside it and are started by resolve.sh.

Somebody works in Resolve on this machine. So: the tests create a project
of their own whose name no human would type, they touch nothing else, and
they put the project that was open back where it was -- also when the test
falls over half way, which is what OwnProject.close() in a finally is for.

What was measured on Resolve 21.0.4.5, on 1.9.2026, and is the reason for
the order in open() and close():

* Only what stands in GetProjectListInCurrentFolder() can be loaded
  again. A project that was only created and never saved does not stand
  there, and DeleteProject answers False for it.
* Whether Resolve writes such a project out on the way to another one
  depends on how it is left, and the two ways differ. LoadProject writes
  it out -- under the name it had, not one of Resolve's choosing -- and
  from then on it is in the list and DeleteProject answers True.
  CreateProject does not: the unsaved project is gone, and no name
  fetches it back. Measured with one project each way.
* Creating is what these tests do, so what is open beforehand is only
  remembered when it already stands in the list, and where it does not
  the test leaves itself out before anything is made. Otherwise the
  first thing a test does is take somebody's unsaved work away for good.
  That is the same rule sweep.py --which applies, and both read the same
  list to decide.
* The tests' own project is saved the moment it is made, so it is really
  there from then on rather than only after somebody opened something
  else.
* DeleteProject refuses a project that is open, so the project that was
  open before is loaded again first -- which is what has to happen anyway.
"""
import os
import random
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
ROOT = os.path.dirname(TESTS)
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    ROOT, "videopodcast-magic.py")


def program():
    """Load the program under test, in English."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
    vpm = importlib.util.module_from_spec(spec)
    sys.modules["vpm"] = vpm
    spec.loader.exec_module(vpm)
    vpm.set_language("en")
    return vpm


# The shape of a name the tests give their own projects -- and nothing
# else. Anchored at both ends, and the whole tail spelled out: after
# "vpm-test-" there has to be a word, then a process id, then four
# hexadecimal digits. A person's own project cannot take that shape by
# accident, and a substring match on "vpm-test" could: the sweep below
# deletes what this matches, so it is written to be narrow rather than
# convenient.
TEST_PROJECT = re.compile(r"^vpm-test-[a-z0-9]+-[0-9]+-[0-9a-f]{4}$")


def a_test_name(what):
    """The name a test gives its own project. The only place it is built."""
    return "vpm-test-%s-%d-%04x" % (what, os.getpid(), random.getrandbits(16))


def swept(pm):
    """Delete what the tests made. Returns (deleted, left standing).

    Projects and folders both, and only what TEST_PROJECT matches. The
    lists are read again afterwards rather than the answers believed:
    DeleteProject says False for a project that is open or was never
    saved, and True is not evidence either.

    Folders, because a run that died half way through leaves one rather
    than a project -- and a folder stands in no project list, so a sweep
    that read only that one could never take it away however often it
    ran. Measured on Resolve 21.0.4.5 on 1.9.2026: DeleteFolder answers
    True for a folder it deleted and False for a name that was never
    there, and it takes a folder with a project still inside it, which is
    the case that matters. It is as narrow as the deleting of projects,
    and no narrower: a folder a person named cannot take this shape.

    A project that is open cannot be deleted, so whoever calls this opens
    something else first -- sweep.py does, and puts the caller's own
    project back afterwards.
    """
    here = pm.GetCurrentProject()
    here = here.GetName() if here else ""
    mine = [n for n in (pm.GetProjectListInCurrentFolder() or [])
            if TEST_PROJECT.match(n)]
    for name in mine:
        # Resolve refuses to delete the project it has open, and answers
        # False without saying why. Skipped here so that it comes back as
        # one that stayed, with a name on it.
        if name == here:
            continue
        try:
            pm.DeleteProject(name)
        except Exception:
            pass
    ours = [n for n in (pm.GetFolderListInCurrentFolder() or [])
            if TEST_PROJECT.match(n)]
    for name in ours:
        try:
            pm.DeleteFolder(name)
        except Exception:
            pass
    mine += ours
    after = ((pm.GetProjectListInCurrentFolder() or [])
             + (pm.GetFolderListInCurrentFolder() or []))
    return ([n for n in mine if n not in after],
            [n for n in mine if n in after])


def leave_out(why):
    """Say out loud that nothing was checked, and stop.

    Not sys.exit(0): a test that bows out and returns 0 cannot be told
    from one that checked everything. resolve.sh reads the 2.
    """
    print("SKIPPED: %s" % why)
    sys.exit(2)


def a_resolve(vpm):
    """Return a running Resolve, or leave the test out saying why."""
    try:
        return vpm.connect_to_resolve()
    except RuntimeError as e:
        leave_out("%s -- start DaVinci Resolve and set Preferences > "
                  "System > General > external scripting to 'Local'"
                  % str(e).replace("\n", " "))


def fixture(name):
    """One of the shared fixture folders fixtures.sh builds."""
    root = os.environ.get("VPM_FIXTURES")
    if not root:
        root = os.path.join("/tmp", "vpm-fixtures-%s" % os.getuid())
    return os.path.join(root, name)


def cameras_of(folder):
    """The camera files of a fixture folder, sorted. Read, never written."""
    return sorted(os.path.join(folder, n) for n in os.listdir(folder)
                  if n.endswith(".mov"))


def standstill(look, wants, patience=20.0, step=0.2):
    """Wait until look() answers wants, giving up when it stops moving.

    On a condition, never on the clock: patience counts from the last time
    the answer changed, so a slow machine is not punished and something
    hanging while there is still time left is still caught. Returns
    (arrived, what was last seen, how long it stood still) -- the caller
    checks it, because exhausted patience is red and not green.
    """
    began = time.time()
    last, since = look(), time.time()
    while last != wants:
        time.sleep(step)
        now = look()
        if now != last:
            last, since = now, time.time()
        elif time.time() - since > patience:
            break
    return last == wants, last, time.time() - began


def progresses(look, done, patience=30.0, step=0.2):
    """Wait until done(seen), giving up when seen stops changing.

    The same discipline as standstill, for a sign of life that is a word
    rather than a number: patience counts from the last time the answer
    changed, so a slow machine is not punished and something hanging
    while there is still time left is caught all the same. Returns
    (arrived, what was last seen, how long it took) -- the caller checks
    it, because exhausted patience is red and not green.
    """
    began = time.time()
    last, since = look(), time.time()
    while not done(last):
        time.sleep(step)
        now = look()
        if now != last:
            last, since = now, time.time()
        elif time.time() - since > patience:
            break
    return done(last), last, time.time() - began


class OwnProject(object):
    """A Resolve project belonging to this test alone, gone again after.

    Its name carries vpm-test, the process id and a random ending, so it
    can be told from anything a person made and two runs cannot collide.
    """

    def __init__(self, vpm, resolve, what):
        self.vpm = vpm
        self.pm = resolve.GetProjectManager()
        self.name = a_test_name(what)
        self.before = None
        self.project = None
        self.kind = None

    def open(self):
        """Create the project and leave it open. Nothing else is touched.

        Only a name that stands in the project manager's list is
        remembered, because that list is the whole of what LoadProject
        can fetch back -- the same rule sweep.py --which applies. Where
        nothing can be remembered the test is left out here, before
        anything is created: creating a project would take an unsaved one
        away for good, and the leaving out has to happen while there is
        still nothing to put back.
        """
        was = self.pm.GetCurrentProject()
        was = was.GetName() if was else ""
        if was not in (self.pm.GetProjectListInCurrentFolder() or []):
            # Before self.before is set, and not only for tidiness: a
            # sys.exit in here runs the caller's finally, and close() must
            # find nothing there that it would try to load again.
            leave_out(
                "Resolve is on %r, which stands in no project list -- only "
                "what stands in that list can be loaded again, so nothing "
                "here could be put back afterwards, and making a project now "
                "would take an unsaved one away for good. Open a project of "
                "your own in Resolve, or save the one that is open, and run "
                "again." % was)
        self.before = was
        self.project, self.kind = self.vpm.open_or_create_project(
            self.pm, self.name, None)
        # Saved at once: unsaved, it is in no list and cannot be deleted
        # again, and a test that fell over would leave it open in front of
        # somebody who did not ask for it.
        self.pm.SaveProject()
        return self.project

    def listed(self):
        """Whether the project manager knows this project by name."""
        return self.name in (self.pm.GetProjectListInCurrentFolder() or [])

    def close(self):
        """Put everything back. Returns "" when it did, else what is left.

        Never raises: it runs in a finally, and a cleanup that throws would
        hide the fault the test was about.
        """
        left = []
        try:
            if self.project is not None:
                self.pm.SaveProject()
                self.pm.CloseProject(self.project)
        except Exception as e:
            left.append("could not close: %s" % e)
        try:
            # Back to what the person had open, before the deleting: a
            # project that is open cannot be deleted.
            if self.before:
                if not self.pm.LoadProject(self.before):
                    left.append("could not open %r again" % self.before)
        except Exception as e:
            left.append("could not open %r again: %s" % (self.before, e))
        try:
            self.pm.DeleteProject(self.name)
            # The answer is not the evidence -- the list is. A project that
            # was never saved is in no list, and DeleteProject says False
            # for it although there is nothing left to delete.
            if self.listed():
                left.append("%r is still in the project list" % self.name)
        except Exception as e:
            left.append("could not delete %r: %s" % (self.name, e))
        return "; ".join(left)
