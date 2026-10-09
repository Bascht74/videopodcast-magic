# -*- coding: utf-8 -*-
"""On a Mac a written file is shown selected in Finder, a folder opened.

open_in_file_manager is what the output tab's button calls. Nothing is
started: subprocess.Popen is replaced by a stand-in that notes what it
was handed, and sys.platform is set to the Mac's for the call, so the
verdict is the same on every machine. In order: a file is handed to
"open -R" and the call says yes, a folder to "open" itself, and a
starter that cannot be found gives no while raising nothing. Limit:
the Windows and Linux branches are left to the builder's own jobs.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import shutil
import subprocess
import tempfile
import time
import the_program

SCRIPT = the_program.SCRIPT
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


folder = tempfile.mkdtemp(prefix="vpm_shown_")
written = os.path.join(folder, "episode.mov")
open(written, "wb").close()
started = []


class Starter(object):
    """Stands in for Popen: notes the command and starts nothing."""

    def __init__(self, cmd, *args, **kwargs):
        started.append(cmd)


class Missing(object):
    """Stands in for Popen on a machine where the starter is not there."""

    def __init__(self, cmd, *args, **kwargs):
        started.append(cmd)
        raise OSError(2, "No such file or directory", cmd[0])


def shown(path, popen):
    """Call the program with this stand-in on a Mac; (answer, commands)."""
    del started[:]
    real_popen, real_platform = subprocess.Popen, sys.platform
    subprocess.Popen, sys.platform = popen, "darwin"
    try:
        answer = vpm.open_in_file_manager(path)
    except Exception as e:
        answer = "raised %s" % type(e).__name__
    finally:
        subprocess.Popen, sys.platform = real_popen, real_platform
    return answer, list(started)


answer, cmds = shown(written, Starter)
check("a written file is shown selected in Finder",
      answer is True and cmds == [["open", "-R", written]],
      "answer %r, started %r" % (answer, cmds))
answer, cmds = shown(folder, Starter)
check("a folder is opened in Finder itself",
      answer is True and cmds == [["open", folder]],
      "answer %r, started %r" % (answer, cmds))
answer, cmds = shown(written, Missing)
check("a starter that cannot be found gives no and raises nothing",
      answer is False and len(cmds) == 1,
      "answer %r after %d attempts" % (answer, len(cmds)))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
