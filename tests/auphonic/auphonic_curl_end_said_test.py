# -*- coding: utf-8 -*-
"""A curl that fails or is stopped is said in its own words, and ended.

_curl_call in this process, with curl stood in for by a small Python
script started in its place: the piece's subprocess calls are routed
there, on every system, and the script answers as a mode says. Sections:
a short call that fails raises with curl's words, or with its return
code where it said nothing; an upload that fails raises with curl's own
last words and not its progress table; and Stop, wanted before the
transfer, ends curl at once and leaves no answer file behind. Nothing
leaves the machine: the script talks to nobody.
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
import contextlib
import io
import shutil
import subprocess
import tempfile
import time
import types
import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")
vpm.show_progress = lambda text, share=None: None

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-62s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


ROOM = tempfile.mkdtemp(prefix="vpm_curl_end_")
ANSWERS = os.path.join(ROOM, "answers")
os.makedirs(ANSWERS)
STANDIN = os.path.join(ROOM, "curl_standin.py")
FAILED = "curl: (6) Could not resolve host: auphonic.com"
BROKEN = "curl: (55) Send failure: Broken pipe"
TABLE = ("100  4096  100  4096    0     0   8192      0 --:--:-- "
         "--:--:-- --:--:--  8192")
with open(STANDIN, "w") as f:
    f.write("\n".join([
        "import os, sys, time",
        "sys.stdin.read()          # the key line, as curl reads it",
        "mode = os.environ['VPM_CURL_MODE']",
        "if mode == 'fail':",
        "    sys.stderr.write(%r + '\\n')" % FAILED,
        "    sys.exit(6)",
        "if mode == 'mute':",
        "    sys.exit(7)",
        "if mode == 'broken':",
        "    sys.stderr.write('  % Total    % Received % Xferd\\n')",
        "    sys.stderr.write(%r + '\\r')" % TABLE,
        "    sys.stderr.write(%r)" % BROKEN,
        "    sys.exit(55)",
        "if mode == 'slow':",
        "    time.sleep(20)",
        "    sys.exit(0)",
        ""]))

PIECE = vpm._curl_call.__globals__
REAL = subprocess


def routed(cmd):
    """curl's command line with the stand-in in curl's place."""
    if cmd and cmd[0] == "curl":
        return [sys.executable, STANDIN] + list(cmd[1:])
    return cmd


PIECE["subprocess"] = types.SimpleNamespace(
    Popen=lambda cmd, *a, **k: REAL.Popen(routed(cmd), *a, **k),
    run=lambda cmd, *a, **k: REAL.run(routed(cmd), *a, **k),
    PIPE=REAL.PIPE, DEVNULL=REAL.DEVNULL,
    CompletedProcess=REAL.CompletedProcess)
# The answer file goes where this test can count what is left of it.
tempfile.tempdir = ANSWERS


def call(mode, progress=False):
    """One _curl_call with the stand-in in *mode*: (error, seconds)."""
    os.environ["VPM_CURL_MODE"] = mode
    start = time.time()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            vpm._curl_call("FAKEKEY-0000",
                           ["https://auphonic.com/api/user.json"],
                           progress=progress)
        error = ""
    except Exception as why:     # the failure is what is judged here
        error = "%s: %s" % (type(why).__name__, why)
    # On Windows curl's words arrive with \r\n; the words are what is judged
    return error.replace("\r\n", "\n"), time.time() - start


print("1. A short call that fails")
error, _s = call("fail")
check("a failed call raises with curl's own words",
      error == "RuntimeError: %s\n" % FAILED,
      "raised %r, wanted %r" % (error, "RuntimeError: %s\n" % FAILED))
error, _s = call("mute")
want = "RuntimeError: " + vpm.T('curl ended with %d') % 7
check("a curl that ends saying nothing is named by its return code",
      error == want, "raised %r, wanted %r" % (error, want))

print("\n2. An upload that fails")
error, _s = call("broken", progress="Uploading")
check("a failed upload raises with curl's last words",
      error.startswith("RuntimeError: ") and error.endswith(BROKEN),
      "raised %r, wanted it to end on %r" % (error, BROKEN))
check("and leaves curl's progress table out of them",
      TABLE.split()[1] not in error and BROKEN in error,
      "raised %r, which carries the table's %r: %s"
      % (error, TABLE.split()[1], TABLE.split()[1] in error))

print("\n3. Stop, wanted before the transfer")
vpm.RUN_STOP["wanted"] = True
try:
    error, seconds = call("slow", progress="Uploading")
finally:
    vpm.RUN_STOP["wanted"] = False
check("a stop wanted before an upload ends curl at once",
      error.startswith("Stopped") and seconds < 10,
      "raised %r after %.1f s, the stand-in would run 20 s"
      % (error, seconds))
left = sorted(os.listdir(ANSWERS))
check("and the stopped upload leaves no answer file behind",
      not left, "left in the answer folder: %r" % left)

tempfile.tempdir = None
shutil.rmtree(ROOM, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
