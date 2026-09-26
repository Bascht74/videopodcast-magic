# -*- coding: utf-8 -*-
"""On Windows the window's end skips the teardown and keeps what it owes.

Sections: on a stand-in Windows the end leaves through os._exit with the
window's code, after the atexit handlers ran and the console and the log
were flushed; anywhere else it hands the code back and touches nothing;
and main() sends the window's code through that door. Each end runs in a
child, since os._exit takes the process with it. The crash it avoids
cannot happen here: this holds the door, not the Windows teardown.
"""
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

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    """One judgement: a line in the report, and a name in bad if it fell."""
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# The child leaves unflushed text in its console and in a log handle,
# puts a marker behind atexit, and asks the door as the platform named.
CHILD = """
import atexit, os, sys, types
sys.path.insert(0, %r)
import the_program
vpm = the_program.load()
where, marker, log = sys.argv[1:4]
atexit.register(lambda: open(marker, "w").close())
handle = open(log, "w", buffering=1 << 20)
handle.write("LOG-TAIL")
vpm._LOG_ASIDE.append(handle)
sys.stdout.write("CONSOLE-TAIL")
vpm.sys = types.SimpleNamespace(platform=where, stdout=sys.stdout,
                                stderr=sys.stderr)
back = vpm.leave_window(7)
vpm.sys = sys
sys.stdout.write("|returned %%r, marker %%s" %% (back, os.path.exists(marker)))
sys.stdout.flush()
os._exit(99)
""" % HERE

# The window stands in as a code, the redirect as nothing, and the door
# as a line that names what it was handed. Not 7: that one is the
# window's own "again, in another language", and main() starts over.
DRIVER = ("import sys;sys.path.insert(0, %r);"
          "import the_program;vpm = the_program.load();"
          "vpm.gui = lambda: 3;vpm.redirect_console = lambda: None;"
          "vpm.leave_window = lambda c: (print('door %%r' %% c), 5)[1];"
          "sys.argv = ['videopodcast-magic'];"
          "raise SystemExit(vpm.main())") % HERE


def run(argv):
    """A child's code, what it said and what went wrong -- never a raise."""
    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    try:
        ran = subprocess.run([sys.executable] + argv, env=env,
                             capture_output=True, text=True, timeout=240)
    except (OSError, subprocess.TimeoutExpired) as e:
        return -1, "", str(e)
    return ran.returncode, ran.stdout, ran.stderr


work = tempfile.mkdtemp(prefix="vpm_winexit_")
script = os.path.join(work, "child.py")
with open(script, "w", encoding="utf-8") as f:
    f.write(CHILD)


def end_as(where):
    """The child's end on that platform: code, console, log, marker."""
    marker = os.path.join(work, where + ".ran")
    log = os.path.join(work, where + ".log")
    code, said, wrong = run([script, where, marker, log])
    kept = open(log, encoding="utf-8").read() if os.path.exists(log) else ""
    return code, said, wrong[-200:], kept, os.path.exists(marker)


try:
    print("\n1. On Windows the end leaves through os._exit")
    code, said, wrong, kept, ran = end_as("win32")
    check("on Windows the window's end leaves with the window's code",
          code == 7 and "|returned" not in said,
          "code %d against 7, said %r, wrong %r" % (code, said[-80:], wrong))
    check("and the atexit handlers ran before it", ran,
          "marker %s after code %d" % (ran, code))
    check("and the console was flushed before it", "CONSOLE-TAIL" in said,
          "the console said %r" % said[-80:])
    check("and the log handle was flushed before it", kept == "LOG-TAIL",
          "the log holds %r against 'LOG-TAIL'" % kept[-80:])

    print("\n2. Anywhere else the code comes back and nothing is touched")
    code, said, wrong, kept, ran = end_as("darwin")
    check("on macOS the end hands the code back and leaves the teardown",
          code == 99 and said.endswith("|returned 7, marker False"),
          "code %d against 99, said %r, wrong %r" % (code, said[-80:], wrong))
    code, said, wrong, kept, ran = end_as("linux")
    check("and on Linux the same",
          code == 99 and said.endswith("|returned 7, marker False"),
          "code %d against 99, said %r, wrong %r" % (code, said[-80:], wrong))

    print("\n3. main() sends the window's code through that door")
    code, said, wrong = run(["-c", DRIVER])
    check("main() hands the window's code to the door and returns its word",
          code == 5 and "door 3" in said,
          "code %d against 5, said %r, wrong %r"
          % (code, said[-80:], wrong[-200:]))
finally:
    shutil.rmtree(work, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
