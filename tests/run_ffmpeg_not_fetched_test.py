# -*- coding: utf-8 -*-
"""The program fetches no ffmpeg of its own: it finds one, or says how.

Where nothing else worked, ffmpeg used to be fetched with pip -- a
wheel carrying the two programs inside itself. It wrote into whatever
Python happened to be running, a system one included, and nobody had
been asked. The sections: the source, where no install of ffmpeg is
left to find; and a search with an empty path, which has to end in the
advice for this machine and try nothing on the way. The probe puts a
recorder in place of the two installers, so it says what the program
asked for, not what pip would have made of it.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import ast
import importlib.util
import shutil
import sys
import tempfile
import time

# Qt comes up with the program and must not want a screen; the speaker
# separation fetches a machine-learning environment and is not asked
# for here.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
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


def stop():
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


#--------------------------------------------------------- 1. The source

with open(SCRIPT, encoding="utf-8") as f:
    TREE = ast.parse(f.read(), filename=SCRIPT)

INSTALLER = "_pip_install"


def installs_in(node):
    """Every call to the pip installer under this node, with its words.

    A call is kept as (line, the words it names), so a fresh install
    can be pointed at rather than only counted. Anything that is not a
    plain string -- a variable, a computed name -- comes back as the
    source of that argument, which is what somebody would have to read
    anyway.
    """
    out = []
    for one in ast.walk(node):
        if not isinstance(one, ast.Call):
            continue
        called = one.func
        name = getattr(called, "id", None) or getattr(called, "attr", None)
        if name != INSTALLER:
            continue
        words = [a.value if isinstance(a, ast.Constant)
                 else ast.dump(a)[:40] for a in one.args]
        out.append((one.lineno, words))
    return out


SEARCH = [n for n in ast.walk(TREE)
          if isinstance(n, ast.FunctionDef)
          and n.name == "find_required_tools"]

print("1. The source of the search for the two programs")
check("the search for the two programs is in the file", len(SEARCH) == 1,
      "%d functions called find_required_tools, wanted 1" % len(SEARCH))
if not SEARCH:
    stop()

inside = installs_in(SEARCH[0])
check("no pip install stands in the search for the two programs",
      not inside,
      "%d calls to %s in find_required_tools, wanted 0: %s"
      % (len(inside), INSTALLER, inside[:3]))

everywhere = installs_in(TREE)
named = [one for one in everywhere
         if any("ffmpeg" in str(w).lower() for w in one[1])]
check("and no pip install anywhere in the program names ffmpeg",
      not named,
      "%d of %d calls to %s name it, wanted 0 of %d: %s"
      % (len(named), len(everywhere), INSTALLER, len(everywhere),
         named[:3]))


#---------------------------------------------- 2. A search with nothing

# An empty folder as the whole search path, so the search finds
# nothing and has to do whatever it does when the machine is bare.
# Both installers are replaced first: the recorder says what was asked
# for and refuses it, so this test can install nothing on the machine
# it runs on -- which is the very thing it is about.
EMPTY = tempfile.mkdtemp(prefix="vpm_nopath_")
# The search prepends the program's own folder before it gives up, so
# that folder belongs to what the probe looks in.
PROBE_PATH = EMPTY + os.pathsep + os.path.dirname(os.path.abspath(SCRIPT))

asked_pip = []


def no_install(*packages):
    asked_pip.append(packages)
    return False


def no_manager():
    """The package manager is never really asked from a test."""
    return False


was_path = os.environ.get("PATH", "")
was_pip = vpm._pip_install
was_manager = vpm.install_over_package_manager
ended = "the search came back without saying anything"
try:
    vpm._pip_install = no_install
    vpm.install_over_package_manager = no_manager
    os.environ["PATH"] = EMPTY
    try:
        vpm.find_required_tools()
    except SystemExit as e:
        ended = e.code
finally:
    os.environ["PATH"] = was_path
    vpm._pip_install = was_pip
    vpm.install_over_package_manager = was_manager
    # ignore_errors, because a folder that would not go must not end the
    # test before it has counted what it found.
    shutil.rmtree(EMPTY, ignore_errors=True)

# What the advice has to begin with, out of the catalogue, so the
# reading does not tie itself to one language.
NOT_FOUND = vpm.T('Not found: %s.\nThe programs must be in the search path '
                  'or next to this file (%s).\nHere: %s').split("%s")[0]

print("\n2. A search that has nothing to find")
on_hand = [tool for tool in ("ffmpeg", "ffprobe")
           if shutil.which(tool, path=PROBE_PATH) is not None]
check("the probe really looked where neither program is",
      not on_hand,
      "%d of 2 were within reach of the probe after all: %s"
      % (len(on_hand), on_hand))
check("a search that finds no ffmpeg installs nothing",
      not asked_pip,
      "%d installs asked for, wanted 0: %s"
      % (len(asked_pip), asked_pip[:3]))
check("and it ends by saying where the two programs come from",
      isinstance(ended, str) and ended.startswith(NOT_FOUND)
      and "ffmpeg" in ended and "ffprobe" in ended,
      "it ended on %r, wanted one beginning %r and naming both"
      % (str(ended)[:90], NOT_FOUND))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
