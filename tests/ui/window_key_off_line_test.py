# -*- coding: utf-8 -*-
"""A window run's key stands on no command line, now or at a restart.

The window's line is built by run_argv with a made-up key and sent
through the window's own run loop into main(), stopped at a stand-in
preflight. In order: the run is reached, its line carries no key, the
run holds the key all the same, sys.argv is the window's own again
afterwards, and a restart then starts the program as it was started.
Nothing is uploaded and nothing is started: preflight and execv are
stand-ins.
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
import queue
import shutil
import tempfile
import time
import types

# The material: a camera file main() finds, and a cache beside it, so
# the tidying main() does on its way in touches nothing of the person's.
FOLDER = tempfile.mkdtemp(prefix="vpm_key_line_")
CAMERA = os.path.join(FOLDER, "camera.mov")
open(CAMERA, "wb").close()
os.makedirs(os.path.join(FOLDER, "cache"))
os.environ["VPM_CACHE"] = os.path.join(FOLDER, "cache")

import the_program

began = time.time()
SCRIPT = the_program.SCRIPT
vpm = the_program.load()
vpm.set_language("en")
ui = vpm.window()

KEY = "FAKEKEY-0000"

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


seen = []


def stand_in_preflight(args, audio_paths, video_paths):
    """Stops the run where the preflight would; keeps its line and key.

    The three parameters and no more, as the program's own has them.
    """
    seen.append((list(sys.argv), args.auphonic_key))
    return 1


vpm.run_preflight = stand_in_preflight

print("1. A window run with a key")
line, _plan, _said = vpm.run_argv(
    {"files": [(CAMERA, "video")], "clip_kinds": {}, "multitrack": False,
     "key": KEY, "preset": "Stand-in preset"}, "")
window_start = [SCRIPT, "--lang", "en"]
sys.argv = list(window_start)
state = {"results": [], "running": True, "dry_run": False}
ui.gui_run_loop(line, state, ui.make_log_writer(state, queue.Queue()),
                lambda *a: None, types.SimpleNamespace(run_step=None),
                lambda *a: None, [])
after = list(sys.argv)
sys.argv = [SCRIPT]
check("the window's loop reaches the run once", len(seen) == 1,
      "the stand-in preflight was reached %d times, wanted once; the "
      "window built %s" % (len(seen), "no line" if line is None
                           else "%d words" % len(line)))
run_line, run_key = seen[0] if seen else ([], None)
check("the key stands nowhere on the line the run reads",
      bool(run_line) and KEY not in run_line
      and "--auphonic-api-key" not in run_line,
      "%d words, the key among them %s, --auphonic-api-key among them "
      "%s, wanted False and False" % (len(run_line), KEY in run_line,
                                      "--auphonic-api-key" in run_line))
check("the run holds the key all the same", run_key == KEY,
      "the run's key is %r, wanted %r" % (run_key, KEY))
check("sys.argv is the window's own again after the run",
      after == window_start,
      "sys.argv afterwards has %d words, the key among them %s, wanted "
      "the %d of the window's start" % (len(after), KEY in after,
                                        len(window_start)))

print("\n2. A restart after that run")
# execv replaced for the length of one call: the program is not really
# started, what is judged is the line it would be started with. The
# line in sys.argv is a run's, as it stood while a run went.
execs = []
kept_execv = vpm.os.execv
vpm.os.execv = lambda path, words: execs.append(list(words))
sys.argv = [SCRIPT, "--auphonic-preset", "Stand-in preset", CAMERA]
try:
    vpm.start_again()
finally:
    vpm.os.execv = kept_execv
    sys.argv = [SCRIPT]
bare = [sys.executable, os.path.abspath(vpm.__file__)]
check("a restart starts the program as it was started, bare",
      execs == [bare],
      "%d starts, the first with %d words after the program, wanted one "
      "with none: %r" % (len(execs), len(execs[0]) - 2 if execs else -1,
                         [os.path.basename(w) for w in execs[0][2:]]
                         if execs else None))

shutil.rmtree(FOLDER, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
