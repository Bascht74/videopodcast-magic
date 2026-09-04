# -*- coding: utf-8 -*-
"""The log of a run is where whoever started it can get at it.

Sections: a copy nobody installed writes beside itself; an installed
copy writes where the platform keeps logs and never into the folder
pip owns; VPM_LOGS moves the whole of it; one folder spelled two ways
is still the folder pip owns; a start without switches says nothing in
front of its window while a start that only reads the switches still
answers; that the file the menu opens is the one this run writes into
and not the copy kept from the run before; and that the Help menu
offers it.

The installed case is rebuilt, not installed: a throwaway environment
is made and the module files are copied into the folder pip would put
them in. Nothing here goes outside, and pip's build step fetches. So
what this proves is what the program looks at -- the folder its file
stands in -- and not pip's own wheel. The second spelling is a link
where the system makes one; the two spellings Windows itself produces
are put to ntpath, which answers here what it answers there.
"""
import glob
import io
import ntpath
import os
import posixpath
import shutil
import subprocess
import sys
import tempfile
import time
import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtGui, QtWidgets

# Where the_program lies, not where this file lies: the child below has
# to import it, and the two are only the same while this file has not
# been copied anywhere.
HERE = os.path.dirname(os.path.abspath(the_program.__file__))
SCRIPT = the_program.SCRIPT
BESIDE = os.path.dirname(os.path.abspath(SCRIPT))

app = QtWidgets.QApplication(sys.argv[:1])
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


# What each platform keeps a log in, written out here rather than
# computed: a test that built the path the way the program builds it
# would only agree with itself.
UNDER_HOME = {"darwin": ("Library", "Logs", "videopodcast-magic"),
              "win32": ("AppData", "Local", "videopodcast-magic", "Logs")}
XDG_STATE = (".local", "state", "videopodcast-magic")

work = tempfile.mkdtemp(prefix="vpm_logreach_")


def child_env(home, extra=None):
    """The environment a child gets: a home of its own, and no leftovers.

    Everything the program reads a log folder out of is pointed into
    the throwaway home, so a run of this test writes nothing into the
    folders of whoever started it.
    """
    env = dict(os.environ)
    env["HOME"] = home
    env["USERPROFILE"] = home
    env["LOCALAPPDATA"] = os.path.join(home, "AppData", "Local")
    env["QT_QPA_PLATFORM"] = "offscreen"
    for name in ("VPM_LOGS", "VPM_SILENT", "XDG_STATE_HOME", "VPM_SCRIPT"):
        env.pop(name, None)
    env.update(extra or {})
    return env


def ask(python, code, env):
    """Run one line of Python in that interpreter and hand back what it said.

    An interpreter that is not there comes back as a code and a
    sentence, never as a raised error: every path here has to reach the
    closing line, or the checks behind the first stumble say nothing.
    """
    try:
        ran = subprocess.run([python, "-c", code], env=env,
                             capture_output=True, text=True)
    except OSError as e:
        return -1, "", str(e)
    return ran.returncode, ran.stdout, ran.stderr


print("\n1. A copy nobody installed keeps its log beside itself")
mine = vpm.log_path()
want = os.path.join(BESIDE, "videopodcast-magic.log")
check("a copy that was not installed says so",
      not vpm.installed_by_a_package_manager(),
      "owner %r for %s" % (vpm.installed_by_a_package_manager(), SCRIPT))
check("its log stands beside the program", mine == want,
      "%s against %s" % (mine, want))

print("\n2. The installed case, rebuilt")
# A bare environment: no pip, nothing fetched, and its site-packages is
# exactly the folder sysconfig calls purelib -- which is the folder the
# program compares its own path against.
nest = os.path.join(work, "installed")
try:
    made = subprocess.run([sys.executable, "-m", "venv", "--without-pip", nest],
                          capture_output=True, text=True)
    built, why = made.returncode, made.stderr[-120:]
except OSError as e:
    # A precondition that cannot be met has to reach the closing line
    # as a judgement. Raised here, it would take the whole file with it
    # and the seventeen checks behind this one would say nothing.
    built, why = -1, str(e)
python = os.path.join(nest, "Scripts" if os.name == "nt" else "bin",
                      "python.exe" if os.name == "nt" else "python")
check("the throwaway environment was built",
      built == 0 and os.path.exists(python),
      "code %d, %s %s, %r" % (built, python,
                              "there" if os.path.exists(python) else "missing",
                              why))
purelib = ""
if os.path.exists(python):
    code, purelib, _e = ask(
        python, "import sysconfig;print(sysconfig.get_paths()['purelib'])",
        child_env(work))
    purelib = purelib.strip()
    os.makedirs(purelib, exist_ok=True)
    # The whole folder, because the program is one: it reads its
    # languages out of language/ beside its way in. models/ stays
    # behind -- 31 MB this test never asks about -- and so does
    # anything a run beside the program has written there.
    shutil.copytree(BESIDE, os.path.join(purelib, "videopodcast_magic"),
                    ignore=shutil.ignore_patterns("models", "__pycache__",
                                                  "*.log", ".DS_Store"))
check("the program lies in the folder pip installs into",
      bool(purelib) and os.path.isfile(
          os.path.join(purelib, "videopodcast_magic", "__init__.py")),
      "purelib %s" % (purelib or "not asked"))

home = os.path.join(work, "home")
os.makedirs(home, exist_ok=True)
SAY = ("import videopodcast_magic as v;"
       "print(bool(v.installed_by_a_package_manager()));"
       "print(v.log_path())")
code, said, went_wrong = ask(python, SAY, child_env(home))
rows = said.splitlines()
check("the installed copy knows it was installed",
      code == 0 and rows[:1] == ["True"],
      "code %d, said %r, wrong %r" % (code, rows[:1], went_wrong[-200:]))
where = rows[1] if len(rows) > 1 else ""
# Both sides through realpath: on a Mac the temporary folder is reached
# through a link, and two spellings of one folder would let this pass
# while the log sat squarely inside it.
inside = (bool(where) and bool(purelib)
          and os.path.realpath(where).startswith(
              os.path.realpath(purelib) + os.sep))
check("its log does not land in the folder pip owns",
      bool(where) and bool(purelib) and not inside,
      "%s against %s" % (where or "nothing", purelib or "no folder"))
wanted = os.path.join(home, *UNDER_HOME.get(sys.platform, XDG_STATE))
wanted = os.path.join(wanted, "videopodcast-magic.log")
check("its log lands where this system keeps logs", where == wanted,
      "%s against %s" % (where or "nothing", wanted))

elsewhere = os.path.join(work, "elsewhere")
code, said, went_wrong = ask(python, SAY,
                             child_env(home, {"VPM_LOGS": elsewhere}))
rows = said.splitlines()
moved = rows[1] if len(rows) > 1 else ""
want_moved = os.path.join(elsewhere, "videopodcast-magic",
                          "videopodcast-magic.log")
check("VPM_LOGS moves the log of an installed copy", moved == want_moved,
      "%s against %s" % (moved or "nothing", want_moved))

print("\n3. One folder, two spellings")
# The names are written out rather than built from purelib: what went
# wrong on Windows was that the package's own path said lib where
# sysconfig said Lib, and ntpath answers here what it answers there.
OWNED = "D:\\a\\vpm\\installed\\Lib\\site-packages"
UNDER = ("D:\\a\\vpm\\installed\\lib\\site-packages"
         "\\videopodcast_magic\\__init__.py")
BESIDE_IT = ("D:\\a\\vpm\\installed\\Lib\\site-packages-old"
             "\\videopodcast_magic\\__init__.py")
POSIX_OWNED = "/x/vpm/installed/Lib/site-packages"
POSIX_UNDER = ("/x/vpm/installed/lib/site-packages"
               "/videopodcast_magic/__init__.py")
check("on a system blind to case, lib and Lib are one folder",
      vpm.inside_folder(UNDER, OWNED, ntpath),
      "%s under %s" % (UNDER, OWNED))
check("on a system that tells case apart, they are two folders",
      not vpm.inside_folder(POSIX_UNDER, POSIX_OWNED, posixpath),
      "%s under %s" % (POSIX_UNDER, POSIX_OWNED))
check("a folder whose name only begins the same is not the one pip owns",
      not vpm.inside_folder(BESIDE_IT, OWNED, ntpath),
      "%s under %s" % (BESIDE_IT, OWNED))

# And the whole program under a second spelling, not only the one
# judgement: a link to the folder pip owns, put in front of the child's
# path, so its file arrives under a name sysconfig never says.
link = os.path.join(work, "another-spelling")
try:
    os.symlink(purelib, link)
    no_link = ""
except OSError as e:
    no_link = str(e)
if no_link:
    print("LEFT OUT: no second spelling of that folder can be made here"
          " -- %s" % no_link)
else:
    code, said, went_wrong = ask(python, SAY,
                                 child_env(home, {"PYTHONPATH": link}))
    rows = said.splitlines()
    check("a copy found under a second spelling knows it was installed",
          code == 0 and rows[:1] == ["True"],
          "code %d, said %r, wrong %r" % (code, rows[:1], went_wrong[-200:]))
    twice = rows[1] if len(rows) > 1 else ""
    check("and its log stays out of the folder pip owns then too",
          bool(twice) and not os.path.realpath(twice).startswith(
              os.path.realpath(purelib) + os.sep),
          "%s against %s" % (twice or "nothing", purelib or "no folder"))

print("\n4. Nothing is said in front of the window")
# The window is replaced by a stand-in that returns at once, and so is
# the redirect that would take the console into the file: what main()
# prints on the way to the window has to stay visible, or this section
# would call a swallowed line silence.
DRIVER = ("import sys;sys.path.insert(0, %r);"
          "import the_program;vpm = the_program.load();"
          "vpm.gui = lambda: 0;vpm.redirect_console = lambda: None;"
          "sys.argv = ['videopodcast-magic'] + %s;"
          "raise SystemExit(vpm.main())")
env = dict(os.environ)
env["QT_QPA_PLATFORM"] = "offscreen"
code, said, went_wrong = ask(sys.executable, DRIVER % (HERE, "[]"), env)
check("a start without switches prints nothing before its window",
      code == 0 and said == "",
      "code %d, %d characters: %r" % (code, len(said), said[:120]))
code, asked, _e = ask(sys.executable, DRIVER % (HERE, "['--version']"), env)
check("a start that only reads the switches still answers",
      asked.strip() != "",
      "%d characters: %r" % (len(asked), asked[:60]))

print("\n5. The log the menu opens is the one this run writes")
# In a child, because the redirect takes the descriptors of whoever
# calls it and this test still has to be able to print. The log is
# pointed at a folder of its own, so nothing here writes into the
# folder of whoever started the run.
kept_folder = os.path.join(work, "rotated")
os.makedirs(kept_folder, exist_ok=True)
ASIDE = ("import sys;sys.path.insert(0, %r);"
         "import os;import the_program;vpm = the_program.load();"
         "vpm.log_path = lambda: os.path.join(%r, 'videopodcast-magic.log');"
         "vpm.log_aside('BEFORE-THE-REDIRECT');"
         "vpm.redirect_console();"
         "vpm.log_aside('AFTER-THE-REDIRECT')") % (HERE, kept_folder)
code, _said, went_wrong = ask(sys.executable, ASIDE, dict(os.environ))


def held(name):
    where = os.path.join(kept_folder, name)
    return (io.open(where, encoding="utf-8").read()
            if os.path.isfile(where) else "")


now, before = held("videopodcast-magic.log"), held("videopodcast-magic_1.log")
check("what is written after the redirect stands in this run's log",
      code == 0 and "AFTER-THE-REDIRECT" in now,
      "code %d, %d characters in the log, wrong %r"
      % (code, len(now), went_wrong[-120:]))
check("and what was written before it stands in the kept one",
      "BEFORE-THE-REDIRECT" in before and "BEFORE-THE-REDIRECT" not in now,
      "%d characters kept, %d in the new log" % (len(before), len(now)))

print("\n6. The window offers the way to the log")
window = QtWidgets.QWidget()
tabs = QtWidgets.QTabWidget()
tabs.addTab(QtWidgets.QWidget(), "One")
player = QtWidgets.QWidget()
player.plays = True
DOES = ("open project", "save project", "close project", "add files",
        "remove", "output folder", "start", "dry run", "settings",
        "mark in", "mark out", "to in", "to out")
opened = []
vpm.open_page = lambda url: opened.append(url) or True

log_here = os.path.join(work, "videopodcast-magic.log")
with open(log_here, "w", encoding="utf-8") as fh:
    fh.write("a line\n")
vpm.log_path = lambda: log_here
menu = vpm.build_menus(QtGui, QtCore, QtWidgets, window, tabs, player,
                       {k: (lambda: None) for k in DOES})
help_menu = [m for m in menu.findChildren(QtWidgets.QMenu)
             if m.title() == vpm.T('&Help')]
check("the Help menu is there", len(help_menu) == 1,
      "%d menus called %r" % (len(help_menu), vpm.T('&Help')))
entries = [a for a in (help_menu[0].actions() if help_menu else [])
           if a.text() == vpm.T('Show the log of this run')]
check("the Help menu offers the log of this run", len(entries) == 1,
      "%d entries called %r among %d"
      % (len(entries), vpm.T('Show the log of this run'),
         len(help_menu[0].actions()) if help_menu else 0))

entry = entries[0] if entries else None
if entry is not None:
    help_menu[0].aboutToShow.emit()
check("the entry names the file the program is writing",
      entry is not None and entry.toolTip() == log_here,
      "%r against %s" % (entry.toolTip() if entry else "no entry", log_here))
check("the entry is alive while there is a log",
      entry is not None and entry.isEnabled(),
      "enabled %s, file %s"
      % (entry.isEnabled() if entry else "no entry", os.path.isfile(log_here)))
if entry is not None:
    entry.trigger()
check("it hands that same file to the opener", opened == [log_here],
      "%r against [%s]" % (opened, log_here))

# No place at all: the program can find none, and then there is nothing
# to open for the whole run.
del opened[:]
vpm.log_path = lambda: None
if entry is not None:
    help_menu[0].aboutToShow.emit()
check("with no place for a log the entry is dead",
      entry is not None and not entry.isEnabled(),
      "enabled %s" % (entry.isEnabled() if entry else "no entry"))
check("and the entry says so instead of a path",
      entry is not None
      and entry.toolTip() == vpm.T('Nothing has been written yet.'),
      "%r against %r" % (entry.toolTip() if entry else "no entry",
                         vpm.T('Nothing has been written yet.')))
# Asked outright, not through the entry: a greyed entry refuses by
# itself, and going through it would measure that grey a second time.
# This is the other guard -- a place that is named and holds no file.
del opened[:]
vpm.log_path = lambda: os.path.join(work, "nothing written here.log")
refused = vpm.log_open()
check("asked with no file at that place, it opens nothing",
      refused is False and opened == [],
      "answer %r, %r handed over" % (refused, opened))

shutil.rmtree(work, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
