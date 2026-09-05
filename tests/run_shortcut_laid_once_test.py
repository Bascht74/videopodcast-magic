# -*- coding: utf-8 -*-
"""One shortcut is laid on the first start, and never a second time.

Where it goes on each of the three systems; that the first start
writes it and says where; that the second says nothing; that one taken
away by hand does not come back; that a place which cannot be written
says why instead of stopping the start; and that a test run lays
nothing unless a home of its own is named. The macOS and the Linux
shape are written here and read back; the Windows one is left out,
because writing a .lnk needs a shell object this machine has not.
"""
import os
import shutil
import sys
import tempfile
import time

import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")
desktop = vpm.beside("desktop", program=vpm.PROGRAM)

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def a_home():
    """A home folder of our own, with a starter pip might have laid."""
    root = tempfile.mkdtemp(prefix="vpm_home_")
    starter = os.path.join(root, "bin", "videopodcast-magic")
    os.makedirs(os.path.dirname(starter))
    with open(starter, "w", encoding="utf-8") as f:
        f.write("#!/bin/sh\nexit 0\n")
    os.chmod(starter, 0o755)
    return root, starter


PICTURE = desktop.icon_bytes()


print("1. Where the pointer would go, on each of the three systems")
ROOT = "/tmp/vpm_nowhere"
want = os.path.join(ROOT, "Applications", "videopodcast-magic.app")
got = desktop.place(root=ROOT, system="darwin")
check("the macOS entry stands in the Applications folder of that home",
      got == want, "%s against %s" % (got, want))

want = os.path.join(ROOT, "AppData", "Roaming", "Microsoft", "Windows",
                    "Start Menu", "Programs", "videopodcast-magic.lnk")
got = desktop.place(root=ROOT, system="nt")
check("the Windows entry stands in the Start menu of that home",
      got == want, "%s against %s" % (got, want))

want = os.path.join(ROOT, ".local", "share", "applications",
                    "videopodcast-magic.desktop")
got = desktop.place(root=ROOT, system="posix")
check("the Linux entry stands where the desktop reads its program list",
      got == want, "%s against %s" % (got, want))


print("\n2. The first start writes it, and says where")
first, starter = a_home()
laid = desktop.make_shortcut(root=first, target=starter, png=PICTURE,
                             system="darwin")
check("the first start writes the entry under the path it names",
      laid.made and os.path.exists(laid.where),
      "made=%s, on disk=%s, at %s"
      % (laid.made, os.path.exists(laid.where), laid.where))

check("the line it says names the place that was written to",
      laid.say == vpm.T('A shortcut to this program was made: %s')
      % laid.where, "it said %r" % laid.say)

points = desktop._points_at(laid.where, "darwin")
check("the runner inside it calls the starter it was handed",
      points == starter, "%s against %s" % (points, starter))

icns = os.path.join(laid.where, "Contents", "Resources",
                    "videopodcast-magic.icns")
check("the picture is written into the entry as a whole icns file",
      os.path.exists(icns)
      and os.path.getsize(icns) == len(PICTURE) + 16,
      "%d bytes against the %d of the picture plus 16"
      % (os.path.getsize(icns) if os.path.exists(icns) else 0,
         len(PICTURE)))


print("\n3. The Linux shape, written here and read back")
lin, lin_starter = a_home()
launcher = desktop.make_shortcut(root=lin, target=lin_starter, png=PICTURE,
                                 system="posix")
points = desktop._points_at(launcher.where, "posix")
check("the launcher names the starter on the line the desktop runs",
      points == lin_starter, "%s against %s" % (points, lin_starter))

themed = os.path.join(lin, ".local", "share", "icons", "hicolor",
                      "256x256", "apps", "videopodcast-magic.png")
check("the picture goes where the icon theme looks for that name",
      os.path.exists(themed)
      and os.path.getsize(themed) == len(PICTURE),
      "%d bytes at %s"
      % (os.path.getsize(themed) if os.path.exists(themed) else 0, themed))

print("LEFT OUT: the Windows link is not written here. A .lnk is written"
      " by the shell object that owns the format, reached through"
      " PowerShell, and this machine has none -- run this test on Windows"
      " to see that piece.")


print("\n4. The second start writes nothing and says nothing")
kept = {desktop.KEPT: laid.where}
stub = os.path.join(laid.where, "Contents", "MacOS", "videopodcast-magic")
before = (os.path.getmtime(stub), os.path.getsize(stub))
time.sleep(0.01)
again = desktop.make_shortcut(root=first, target=starter, png=PICTURE,
                              kept=kept, system="darwin")
check("the second start writes nothing", not again.made,
      "made=%s, and it looked at %s" % (again.made, again.where))
check("the second start says nothing", again.say == "",
      "it said %r" % again.say)
after = (os.path.getmtime(stub), os.path.getsize(stub))
check("what the first start wrote stands there untouched",
      after == before, "%r against %r" % (after, before))
# Settings can be reset or lost. An entry that is found good and never
# written down would then be laid again after the next hand-deletion.
noted = {}
good = desktop.make_shortcut(root=first, target=starter, png=PICTURE,
                             kept={}, write_down=noted.__setitem__,
                             system="darwin")
check("an entry found already good is written down all the same",
      not good.made and noted.get(desktop.KEPT) == laid.where,
      "made=%s, written down %r, wanted %r"
      % (good.made, noted.get(desktop.KEPT), laid.where))


print("\n5. One taken away by hand does not come back")
shutil.rmtree(laid.where)
gone = desktop.make_shortcut(root=first, target=starter, png=PICTURE,
                             kept=kept, system="darwin")
check("a shortcut taken away by hand is not laid a second time",
      not gone.made and not os.path.exists(laid.where),
      "made=%s, on disk=%s" % (gone.made, os.path.exists(laid.where)))
check("and nothing is said about the one that was taken away",
      gone.say == "", "it said %r" % gone.say)

second, other = a_home()
elsewhere = desktop.make_shortcut(root=second, target=other, png=PICTURE,
                                  kept=kept, system="darwin")
check("the same note does not keep a second machine from getting one",
      elsewhere.made and os.path.exists(elsewhere.where),
      "made=%s at %s" % (elsewhere.made, elsewhere.where))


print("\n6. A place that cannot be written says why, the start goes on")
blocked, blocked_starter = a_home()
in_the_way = os.path.join(blocked, "Applications")
with open(in_the_way, "w", encoding="utf-8") as f:
    f.write("not a folder\n")
try:
    stopped = desktop.make_shortcut(root=blocked, target=blocked_starter,
                                    png=PICTURE, system="darwin")
    raised = ""
except Exception as e:
    stopped = None
    raised = "%s: %s" % (type(e).__name__, e)
check("a place that cannot be written stops nothing and raises nothing",
      stopped is not None and not stopped.made,
      "it raised %r" % raised if raised else "made=%s" % stopped.made)
said = stopped.say if stopped is not None else ""
head = vpm.T('No shortcut to this program was made: %s') % ""
check("and it says one line that names the place it could not write",
      said.startswith(head) and in_the_way in said
      and len(said.splitlines()) == 1,
      "%d line(s), %r" % (len(said.splitlines()), said[-70:]))


print("\n7. A run marked as a test lays nothing unless it names a home")
# A home and a starter of our own for this section, so that a guard
# broken for a counter-proof still cannot reach the account this runs
# in: expanduser reads HOME, and no starter means nothing is written.
kept_env = dict((name, os.environ.get(name))
                for name in ("VPM_SHORTCUT", "VPM_SETTINGS", "HOME"))
mine = tempfile.mkdtemp(prefix="vpm_choices_")
os.environ["VPM_SETTINGS"] = mine
os.environ["HOME"] = tempfile.mkdtemp(prefix="vpm_nohome_")
os.environ.pop("VPM_SHORTCUT", None)
vpm.forget_settings()
looked = desktop.command_path
try:
    desktop.command_path = lambda name=None: ""
    quiet = desktop.lay_on_first_start()
    check("a test run with no home of its own lays nothing at all",
          not quiet.made and quiet.where == "",
          "made=%s, where=%r" % (quiet.made, quiet.where))

    named, named_starter = a_home()
    os.environ["VPM_SHORTCUT"] = named
    desktop.command_path = lambda name=None: named_starter
    asked = desktop.lay_on_first_start()
    check("a test run that names one gets a shortcut in it",
          asked.made and os.path.exists(asked.where),
          "made=%s at %s" % (asked.made, asked.where))
    check("and the path it laid is written down for the next start",
          vpm.settings().get(desktop.KEPT) == asked.where,
          "%r against %r" % (vpm.settings().get(desktop.KEPT), asked.where))
finally:
    desktop.command_path = looked
    for name, was in kept_env.items():
        if was is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = was
    vpm.forget_settings()
    shutil.rmtree(mine, ignore_errors=True)


print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
