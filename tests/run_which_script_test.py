# -*- coding: utf-8 -*-
"""The log names the copy of the script that is running.

With two copies on one machine and a log that gives only a file name,
there is no telling which one a run used. In order: the program answers
with a name at all, the name is a full path, the file behind it is
there, it is the file that was loaded and not the one that was invoked,
and last a second copy started in a folder of its own writes that
folder's path into the header of its own log.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
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


def stamp(path):
    """Device and inode of a path, (-1, -1) where there is no file."""
    try:
        st = os.stat(path)
        return (st.st_dev, st.st_ino)
    except (OSError, ValueError, TypeError):
        return (-1, -1)


def one_line(text, limit=120):
    """The last non-empty line of some output, flattened and cut short."""
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    return lines[-1][:limit] if lines else "(nothing)"


# --- what the program says about itself -------------------------------

where = ""
raised = "nothing"
try:
    where = vpm.running_from()
except Exception as exc:                # the answer, not the traceback
    raised = type(exc).__name__

check("the program says which file it was loaded from",
      isinstance(where, str) and where not in ("", "?"),
      "running_from() gave %r, %d characters, raised %s -- wanted a name"
      % (where, len(where) if isinstance(where, str) else -1, raised))

parts = len([p for p in where.split(os.sep) if p]) if where else 0
check("that name is a full path, not a bare file name",
      bool(where) and os.path.isabs(where),
      "%r -- %d characters in %d path parts, isabs=%s, wanted True"
      % (where, len(where), parts, os.path.isabs(where) if where else False))

named = stamp(where)
check("the file that name points at is there",
      named != (-1, -1),
      "%r -- stat gave device/inode %d/%d, wanted a pair above -1"
      % (where, named[0], named[1]))

loaded = stamp(SCRIPT)
check("it names the file that was loaded, not the one invoked",
      named == loaded and named != (-1, -1),
      "named device/inode %d/%d, loaded %d/%d, argv[0] %d/%d -- wanted "
      "named to equal loaded"
      % (named + loaded + stamp(sys.argv[0])))

# --- and what a second copy writes into its own log -------------------

lab = tempfile.mkdtemp(prefix="which-script-")
copy = os.path.join(lab, "a-second-copy.py")
shutil.copyfile(SCRIPT, copy)
log = os.path.join(lab, "videopodcast-magic.log")
CODE = ("import importlib.util, sys\n"
        "s = importlib.util.spec_from_file_location('vpm', sys.argv[1])\n"
        "m = importlib.util.module_from_spec(s)\n"
        "sys.modules['vpm'] = m\n"
        "s.loader.exec_module(m)\n"
        "m.redirect_console()\n")
started = subprocess.run([sys.executable, "-B", "-c", CODE, copy],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
spoke = started.stdout.decode("utf-8", "replace")

check("a second copy of the program starts in a folder of its own",
      started.returncode == 0,
      "the copy returned %d, wanted 0, after %d characters ending %r"
      % (started.returncode, len(spoke), one_line(spoke)))

size = os.path.getsize(log) if os.path.isfile(log) else -1
check("that run leaves a log beside the copy it ran from",
      size > 0,
      "%r -- %d bytes, wanted more than 0, %d files in the folder"
      % (log, size, len(os.listdir(lab))))

head = []
if size > 0:
    with open(log, encoding="utf-8", errors="replace") as fh:
        head = [ln.strip() for ln in fh.read().splitlines()[:3]]
want = os.path.abspath(copy)
at = [i + 1 for i, ln in enumerate(head) if ln == want]
check("the log header names that copy by its full path",
      bool(at),
      "wanted %r (%d characters) among the first %d lines of the log, "
      "found on line %s" % (want, len(want), len(head),
                            at[0] if at else "none"))

shutil.rmtree(lab, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
