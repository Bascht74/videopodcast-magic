# -*- coding: utf-8 -*-
"""Clear away the projects the tests made, and put back what was open.

Somebody works in Resolve on this machine. Every test deletes its own
project in a finally, but a finally does not run when the process is
killed -- a Ctrl-C into a pipe, a SIGPIPE from a `head`, a crash of the
interpreter. Then a vpm-test project stays behind, and the test's project
stays open in front of somebody who did not ask for it.

So resolve.sh calls this twice: once before the tests, where a leftover
from an earlier killed run is the only place it can be found, and once
from its exit trap, so it runs whether the tests passed, failed, threw or
were interrupted. It deletes only what resolve_ground.TEST_PROJECT
matches -- the whole shape of a name the tests build, not a substring --
so a project a person named cannot be hit.

The order is fixed and the last step is the one that matters: open what
was open first (a project that is open cannot be deleted anyway), then
delete, then make sure the right project is open again and say so. If
Resolve will not open it, that is said loudly with the name in it,
because then somebody has to open it by hand.

  python3 sweep.py --which                    print what is open now
  python3 sweep.py --sweep --restore NAME     clear away, put NAME back
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import resolve_ground as ground_of


def open_now(pm):
    p = pm.GetCurrentProject()
    return p.GetName() if p else ""


def main(argv):
    vpm = ground_of.program()
    try:
        resolve = vpm.connect_to_resolve()
    except RuntimeError as e:
        # Not reachable is not a fault here and nothing is deleted: the
        # runner has its own readable line for it.
        print("  no Resolve to tidy up in: %s" % str(e).replace("\n", " "))
        return 2
    pm = resolve.GetProjectManager()
    if "--which" in argv:
        # Never a project of the tests' own shape. Where a run was killed
        # outright no trap could run, and the leftover is then still open
        # -- reporting it would make the next run guard it as if it were
        # somebody's work, and it could then never be deleted.
        here = open_now(pm)
        print("" if ground_of.TEST_PROJECT.match(here) else here)
        return 0

    wanted = ""
    if "--restore" in argv:
        at = argv.index("--restore")
        if at + 1 < len(argv):
            wanted = argv[at + 1]
    if wanted and ground_of.TEST_PROJECT.match(wanted):
        print("  %r is a project the tests made, not somebody's -- it is "
              "not put back." % wanted)
        wanted = ""

    # Nothing of the tests' may be open when the deleting starts: Resolve
    # answers False for the project it has open and leaves it standing.
    here = open_now(pm)
    if wanted and here != wanted:
        pm.LoadProject(wanted)
    elif not wanted and ground_of.TEST_PROJECT.match(here):
        # An earlier run was killed before it could put anything back, so
        # its project is still open and cannot be deleted while it is.
        # Something else is opened instead -- never CloseProject with
        # nothing after it. Measured on Resolve 21.0.4.5: closing the last
        # project leaves the project manager with no database, and then
        # LoadProject, CreateProject and even GetCurrentPage stop
        # answering until somebody attends to the window. That is a worse
        # state to leave a machine in than a project nobody asked for.
        others = [n for n in (pm.GetProjectListInCurrentFolder() or [])
                  if not ground_of.TEST_PROJECT.match(n)]
        if others:
            print("  %r was still open -- an earlier run was killed before "
                  "it could\n  put anything back. Opening %r instead."
                  % (here, others[0]))
            pm.LoadProject(others[0])
        else:
            print("")
            print("  ####################################################")
            print("  # %r is open and there is no other" % here)
            print("  # project to open instead, so it cannot be deleted.")
            print("  # Open another project by hand and run this again.")
            print("  ####################################################")

    gone, left = ground_of.swept(pm) if "--sweep" in argv else ([], [])
    if gone:
        print("  swept %d project%s the tests made: %s"
              % (len(gone), "" if len(gone) == 1 else "s",
                 ", ".join(repr(n) for n in gone)))
    if left:
        print("  COULD NOT DELETE, still in the project list: %s"
              % ", ".join(repr(n) for n in left))
    if "--sweep" in argv and not gone and not left:
        print("  nothing of the tests' was left over.")

    if not wanted:
        print("  nothing was open at the start to put back; Resolve is on "
              "%r." % open_now(pm))
        return 0
    # And last of all: the project that was open at the start is open
    # again. Tried once more where the sweep moved it.
    if open_now(pm) != wanted:
        pm.LoadProject(wanted)
    if open_now(pm) == wanted:
        print("  open again: %r" % wanted)
        return 0
    print("")
    print("  ####################################################")
    print("  # RESOLVE WOULD NOT OPEN %r AGAIN." % wanted)
    print("  # It was open when this run started. Open it by hand;")
    print("  # what is open now is %r." % open_now(pm))
    print("  ####################################################")
    return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
